import json
import os
import re
import uuid

from pydantic import BaseModel

from src.constants import TaskStatus, PRIORITY_SORT_ORDER, STATUS_SORT_ORDER, CATEGORY_SORT_ORDER, TaskCategory
from src.exceptions import TaskDoesNotExists
from src.schemas import TaskCreate, TaskRead, TaskUpdate


class TaskSchemaEncoder(json.JSONEncoder):
    """Custom class for converting pydantic models for a task to json"""

    def default(self, obj):
        if isinstance(obj, BaseModel):
            obj = obj.model_dump(exclude_none=True)
            obj["deadline"] = str(obj["deadline"])

            return obj

        return json.JSONEncoder.default(self, obj)


class TaskService:
    def __init__(self, file_name: str):
        """
        Download data from a file and save it to "self.tasks"

        ## Attributes ##
        :self.file_name: the relative or absolute path to the file
        :self.tasks: the list of tasks received from the file.
        When loading, each task is converted to the pydantic "TaskRead" class
        """

        self.file_name: str = file_name
        self.tasks: list[TaskRead] = self._load_data(file_name)

    @staticmethod
    def _load_data(file_name: str) -> list[TaskRead]:
        """
        Download data about tasks from a file.

        Converts data about each task into an instance of the "TaskRead" class.
        If the file does not exist at the specified path, or it is empty, it
        returns an empty list.
        """

        if os.path.exists(file_name):
            with open(file_name, "r", encoding='utf-8') as file:
                return [TaskRead.model_validate(task) for task in json.load(file)]

        return []

    @staticmethod
    def _basic_sorting_key(task: TaskRead) -> tuple:
        return (
            PRIORITY_SORT_ORDER[task.priority],
            STATUS_SORT_ORDER[task.status],
            task.deadline,
            CATEGORY_SORT_ORDER[task.category],
            task.name
        )

    def save_data(self) -> None:
        """
        Save the current list of "self.tasks" to a file.

        Completely overwrites the file.
        """

        with open(self.file_name, "w", encoding='utf-8') as file:
            json.dump(self.tasks, file, ensure_ascii=False, indent=4, cls=TaskSchemaEncoder)

    def add(self, data: TaskCreate, need_save: bool = True) -> TaskRead:
        """Add a new task to the list."""

        validated_task = TaskRead(id=str(uuid.uuid4()), status=TaskStatus.not_completed, **data.model_dump())
        self.tasks.append(validated_task)

        if need_save:
            self.save_data()

        return validated_task

    def get_all(self) -> list[TaskRead]:
        """Get a sorted list of all tasks"""

        return sorted(self.tasks, key=self._basic_sorting_key)

    def find(self, query: str) -> list[TaskRead]:
        """
        Get a sorted list of tasks whose name or description
        contains one of the specified keywords.
        """

        query = re.sub(r'[^\w\s]', '', query)
        query = re.sub(r' {2,}', ' ', query)
        query = query.strip()

        keywords = query.split(" ")
        query = '|'.join(rf'\b{word}\b' for word in keywords)

        result = []
        for task in self.tasks:
            keywords_in_name = re.findall(query, task.name, re.IGNORECASE)
            if keywords_in_name:
                result.append(task)
                continue

            keywords_in_description = re.findall(query, task.description, re.IGNORECASE)
            if keywords_in_description:
                result.append(task)

        return sorted(result, key=self._basic_sorting_key)

    def get_by_id(self, task_id: str) -> TaskRead | None:
        """Get a task by id."""

        for task in self.tasks:
            if task_id.lower() == task.id.lower():
                return task

        return None

    def get_by_category(self, category: TaskCategory) -> list[TaskRead] | None:
        """Get a sorted list of tasks by category."""

        return [task for task in self.tasks if category == task.category]

    def get_by_status(self, status: TaskStatus) -> list[TaskRead] | None:
        """Get a sorted list of tasks by status."""

        return [task for task in self.tasks if status == task.status]

    def get_by_category_and_status(self, category: TaskCategory, status: TaskStatus) -> list[TaskRead] | None:
        """Get a sorted list of tasks by category and status."""

        return [task for task in self.tasks if category == task.category and status == task.status]

    def delete(self, task_id: str, need_save: bool = True) -> None:
        """
        Delete a task by id.

        If a task with the specified id does not exist, the error
        "TaskDoesNotExists" will be raised.
        """

        task = self.get_by_id(task_id)
        if not task:
            raise TaskDoesNotExists(task_id)

        self.tasks.remove(task)

        if need_save:
            self.save_data()

    def update(self, task_id: str, data: TaskUpdate, need_save: bool = True) -> None:
        """
        Update a task with the specified data.

        If a task with the specified id does not exist, the error
        "TaskDoesNotExists" will be raised.
        """

        for i, task in enumerate(self.tasks):
            if task_id.lower() == task.id.lower():
                task_data = task.model_dump()
                new_data = data.model_dump(exclude_none=True)
                task_data.update(new_data)
                self.tasks[i] = TaskRead.model_validate(task_data)

                if need_save:
                    self.save_data()

                return

        raise TaskDoesNotExists(task_id)
