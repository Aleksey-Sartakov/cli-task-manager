class TaskDoesNotExists(Exception):
    def __init__(self, task_id: str):
        self.msg = f"The task with the id \"{task_id}\" does not exist."

    def __str__(self) -> str:
        return self.msg
