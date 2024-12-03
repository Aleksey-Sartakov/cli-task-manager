from enum import Enum


DATA_FILE = "tasks.json"
DATA_FILE_FOR_TESTS = "test_tasks.json"
TASK_SERVICE_NAME_IN_CLICK_CONTEXT = "task_service"


class TaskStatus(str, Enum):
    completed = "completed"
    not_completed = "not_completed"


class TaskPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"


class TaskCategory(str, Enum):
    work = "work"
    study = "study"
    personal = "personal"


STATUS_SORT_ORDER = {
    TaskStatus.not_completed: 0,
    TaskStatus.completed: 1
}
PRIORITY_SORT_ORDER = {
    TaskPriority.high: 0,
    TaskPriority.normal: 1,
    TaskPriority.low: 2
}
CATEGORY_SORT_ORDER = {
    TaskCategory.work: 0,
    TaskCategory.study: 1,
    TaskCategory.personal: 2
}
