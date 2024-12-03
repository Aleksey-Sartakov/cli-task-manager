from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator, model_serializer

from src.constants import TaskStatus, TaskCategory, TaskPriority


class BaseTaskSchema(BaseModel):
    name: str
    description: str
    category: TaskCategory
    deadline: date
    priority: TaskPriority

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name")
    @classmethod
    def validate_author(cls, value: str):
        if not value.strip():
            raise ValueError("The task must have a name.")

        return value


class TaskCreate(BaseTaskSchema):
    pass


class TaskRead(BaseTaskSchema):
    id: str
    status: TaskStatus

    @model_serializer()
    def serialize_model(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "category": self.category.value,
            "deadline": str(self.deadline)
        }


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: TaskCategory | None = None
    deadline: date | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
