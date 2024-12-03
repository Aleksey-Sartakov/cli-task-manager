from datetime import datetime
import os

import pytest as pytest
from pydantic import ValidationError

from src.constants import DATA_FILE_FOR_TESTS, TaskStatus, TaskCategory, TaskPriority
from src.exceptions import TaskDoesNotExists
from src.schemas import TaskCreate, TaskRead, TaskUpdate
from src.service import TaskService


@pytest.fixture(scope="session")
def task_service() -> TaskService:
    yield TaskService(DATA_FILE_FOR_TESTS)

    if os.path.exists(DATA_FILE_FOR_TESTS):
        os.remove(DATA_FILE_FOR_TESTS)


@pytest.mark.task_service
@pytest.mark.parametrize(
    "name, description, category, deadline, priority",
    [
        ["Task 1", "test task", "work", "2024-12-21", "high"],
        ["Task 2", "", "work", "2024-12-22", "high"],
        ["Task 3", "123", "work", "2024-12-23", "normal"],
        ["Task 8", "test task", "study", "2024-12-22", "normal"],
        ["Task 9", "test task", "study", "2024-12-22", "normal"],
        ["Task 10", "test task", "study", "2024-12-23", "high"],
        ["Task 11", "test task", "study", "2024-12-25", "low"],
        ["Task 12", "test task", "personal", "2024-12-22", "normal"]
    ]
)
def test_add(task_service, name, description, category, deadline, priority):
    result = task_service.add(
        TaskCreate(name=name, description=description, category=category, deadline=deadline, priority=priority),
        need_save=False
    )

    assert isinstance(result, TaskRead)
    assert result.id is not None
    assert result.status == TaskStatus.not_completed


@pytest.mark.task_service
@pytest.mark.parametrize(
    "name, description, category, deadline, priority",
    [
        ["Task 4", 123, "work", "2024-12-20", "low"],
        ["Task 5", "test task", "work", 2024-12-20, "low"],
        ["Task 6", "test task", "work", "2024-20-08", "low"],
        ["Task 7", "test task", "work", "", "low"],
        [123, "test task", "personal", "2024-12-22", "normal"],
        ["", "test task", "personal", "2024-12-22", "normal"],
        ["Task 13", "test task", "personal", "2024 12 22", "normal"],
        ["Task 14", "test task", "personal", "2024:12:22", "normal"]
    ]
)
def test_add_failed(task_service, name, description, category, deadline, priority):
    with pytest.raises(ValidationError):
        task_service.add(
            TaskCreate(name=name, description=description, category=category, deadline=deadline, priority=priority),
            need_save=False
        )


@pytest.mark.task_service
def test_get_all(task_service):
    tasks = task_service.get_all()

    assert len(tasks) == 8
    assert (tasks[0].name == "Task 1" and tasks[2].name == "Task 10" and
            tasks[3].name == "Task 8" and tasks[-1].name == "Task 11")


@pytest.mark.task_service
def test_get_by_id(task_service):
    task = task_service.add(
        TaskCreate(
            name="Test get task",
            description="test get task",
            category=TaskCategory.work,
            deadline="2025-01-01",
            priority=TaskPriority.high
        ),
        need_save=False
    )
    found_task = task_service.get_by_id(task.id)

    assert task == found_task

    not_existing_task = task_service.get_by_id("1")

    assert not_existing_task is None


@pytest.mark.task_service
def test_get_by_id_not_valid_id_type(task_service):
    with pytest.raises(AttributeError):
        task_service.get_by_id(1)


@pytest.mark.task_service
def test_update(task_service):
    new_name = "Updated name"
    new_description = "new description"
    new_deadline = "2024-12-20"

    task = task_service.add(
        TaskCreate(
            name="Test update task",
            description="test update task",
            category=TaskCategory.work,
            deadline="2025-01-01",
            priority=TaskPriority.high
        ),
        need_save=False
    )

    task_service.update(task.id, TaskUpdate(status=TaskStatus.completed), need_save=False)

    found_task = task_service.get_by_id(task.id)

    assert found_task.status == TaskStatus.completed

    task_service.update(
        task.id,
        TaskUpdate(name=new_name, description=new_description, deadline=new_deadline),
        need_save=False
    )

    found_task = task_service.get_by_id(task.id)

    assert (found_task.name == new_name and found_task.description == new_description and
            found_task.deadline == datetime.strptime(new_deadline, "%Y-%m-%d").date())


@pytest.mark.task_service
def test_update_task_does_not_exist(task_service):
    with pytest.raises(TaskDoesNotExists):
        task_service.update("1",  TaskUpdate(status=TaskStatus.completed), need_save=False)


@pytest.mark.task_service
@pytest.mark.parametrize(
    "category, tasks_count",
    [
        [TaskCategory.work, 5],
        [TaskCategory.personal, 1],
        ["some category", 0]
    ]
)
def test_get_by_category(task_service, category, tasks_count):
    found_tasks = task_service.get_by_category(category)
    assert len(found_tasks) == tasks_count


@pytest.mark.task_service
@pytest.mark.parametrize(
    "status, tasks_count",
    [
        [TaskStatus.completed, 1],
        [TaskStatus.not_completed, 9],
        ["some status", 0]
    ]
)
def test_get_by_status(task_service, status, tasks_count):
    found_tasks = task_service.get_by_status(status)
    assert len(found_tasks) == tasks_count


@pytest.mark.task_service
def test_get_by_category_and_status(task_service):
    found_tasks = task_service.get_by_category(TaskCategory.work)
    task_service.update(found_tasks[0].id, TaskUpdate(status=TaskStatus.completed), need_save=False)

    found_tasks = task_service.get_by_category(TaskCategory.personal)
    task_service.update(found_tasks[0].id, TaskUpdate(status=TaskStatus.completed), need_save=False)

    found_tasks = task_service.get_by_category_and_status(TaskCategory.work, TaskStatus.completed)
    assert len(found_tasks) == 2

    found_tasks = task_service.get_by_category_and_status(TaskCategory.personal, TaskStatus.completed)
    assert len(found_tasks) == 1

    found_tasks = task_service.get_by_category_and_status(TaskCategory.personal, TaskStatus.not_completed)
    assert len(found_tasks) == 0

    found_tasks = task_service.get_by_category_and_status(TaskCategory.personal, "some status")
    assert len(found_tasks) == 0


@pytest.mark.task_service
def test_delete(task_service):
    task = task_service.add(
        TaskCreate(
            name="Test update task",
            description="test update task",
            category=TaskCategory.work,
            deadline="2025-01-01",
            priority=TaskPriority.high
        ),
        need_save=False
    )

    found_task = task_service.get_by_id(task.id)
    assert found_task == task

    task_service.delete(task.id, need_save=False)

    task = task_service.get_by_id(task.id)
    assert task is None


@pytest.mark.task_service
def test_delete_task_does_not_exist(task_service):
    with pytest.raises(TaskDoesNotExists):
        task_service.delete("1", need_save=False)


@pytest.mark.task_service
@pytest.mark.parametrize(
    "query, tasks_count",
    [
        ["task", 9],
        ["get", 1],
        ["get task", 9],
        ["tasks", 0],
        ["updated   task", 10],
        ["get, update", 1],
        ["%get  &  updated!", 2],
        [" get  ", 1]
    ]
)
def test_find(task_service, query, tasks_count):
    tasks = task_service.find(query)
    assert len(tasks) == tasks_count


@pytest.mark.task_service
def test_save_data(task_service):
    task_service.save_data()

    another_task_service = TaskService(DATA_FILE_FOR_TESTS)

    tasks = another_task_service.get_all()
    assert len(tasks) == 10
