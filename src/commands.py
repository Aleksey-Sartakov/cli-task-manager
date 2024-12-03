import click
from pydantic import ValidationError

from src.constants import TASK_SERVICE_NAME_IN_CLICK_CONTEXT, DATA_FILE, TaskCategory, TaskStatus
from src.exceptions import TaskDoesNotExists
from src.schemas import TaskCreate, TaskUpdate
from src.service import TaskService


@click.group()
@click.pass_context
def app(ctx) -> None:
    """
    The entry point for task manager.

    An instance of the "TaskService" class is initialized.
    This instance is available to all commands within the same session.
    """

    ctx.ensure_object(dict)
    ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]: TaskService = TaskService(DATA_FILE)


@app.command()
@click.argument("name")
@click.argument("description")
@click.argument("category")
@click.argument("deadline")
@click.argument("priority")
@click.pass_context
def add(ctx, name: str, description: str, category: str, deadline: str, priority: str) -> None:
    """
    Create a new task.

    :param name: the name of the task

    :param description: the description of the task

    :param category: the name of the category. It can take
    one of the following values ["work", "study", "personal"]

    :param deadline: the date string in the format "YYYY-MM-DD"

    :param priority: It can take one of the following values
    ["work", "study", "personal"]
    """

    task_service = ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]

    try:
        task = task_service.add(
            TaskCreate(name=name, description=description, category=category, deadline=deadline, priority=priority)
        )

        click.echo(f"The task \"{task.name}\" successfully added with id = {task.id}")

    except ValidationError as e:
        click.echo(f"Validation error. The arguments passed do not meet the requirements:\n{e}")

    except Exception as e:
        click.echo(f"Unknown error:\n{e}")


@app.command()
@click.pass_context
def get_all(ctx) -> None:
    """Get a sorted list of all tasks."""

    task_service: TaskService = ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]
    tasks = task_service.get_all()

    if not tasks:
        click.echo("There are no tasks.")
    else:
        for task in tasks:
            click.echo(task.model_dump())


@app.command()
@click.argument("task_id")
@click.pass_context
def get_by_id(ctx, task_id: str) -> None:
    """Get information about a task by id."""

    task_service: TaskService = ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]
    task = task_service.get_by_id(task_id)

    if not task:
        click.echo(f"The task with id '{task_id}' could not be found.")
    else:
        click.echo(task.model_dump())


@app.command()
@click.argument("category")
@click.pass_context
def get_by_category(ctx, category: TaskCategory) -> None:
    """Get a sorted list of tasks with specified category value."""

    task_service: TaskService = ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]
    tasks = task_service.get_by_category(category)

    if not tasks:
        click.echo(f"There are no tasks with the category '{category}'.")
    else:
        for task in tasks:
            click.echo(task.model_dump())


@app.command()
@click.argument("status")
@click.pass_context
def get_by_status(ctx, status: TaskStatus) -> None:
    """Get a sorted list of tasks with specified status value."""

    if status not in [TaskStatus.completed, TaskStatus.not_completed]:
        click.echo(f"A status must be in {[TaskStatus.completed, TaskStatus.not_completed]}.")

        return

    task_service: TaskService = ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]
    tasks = task_service.get_by_status(status)

    if not tasks:
        click.echo(f"There are no tasks with the status '{status}'.")
    else:
        for task in tasks:
            click.echo(task.model_dump())


@app.command()
@click.argument("category")
@click.argument("status")
@click.pass_context
def get_by_category_and_status(ctx, category: TaskCategory, status: TaskStatus) -> None:
    """Get a sorted list of tasks with specified category and status values."""

    task_service: TaskService = ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]
    tasks = task_service.get_by_category_and_status(category, status)

    if not tasks:
        click.echo(f"There are no tasks with the category '{category}' and status '{status}'.")
    else:
        for task in tasks:
            click.echo(task.model_dump())


@app.command()
@click.argument("query")
@click.pass_context
def find(ctx, query: str) -> None:
    """
    Get a sorted list of tasks that match the specified query.

    The query is divided into separate words. If at least one
    of the words is contained in the title or description of
    the task, then this task is included in the resulting list.
    """

    task_service: TaskService = ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]
    tasks = task_service.find(query)

    if not tasks:
        click.echo(f"There are no tasks matching the query '{query}'.")
    else:
        for task in tasks:
            click.echo(task.model_dump())


@app.command()
@click.argument("task_id")
@click.pass_context
def delete(ctx, task_id: str) -> None:
    """Delete a task by id."""

    task_service: TaskService = ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]

    try:
        task_service.delete(task_id)

        click.echo(f"The task with id \"{task_id}\" has been successfully deleted.")

    except TaskDoesNotExists as e:
        click.echo(e)

    except Exception as e:
        click.echo(f"Unknown error:\n{e}")


@app.command()
@click.argument("task_id")
@click.option("--name", "-n", default=None)
@click.option("--description", "-d", default=None)
@click.option("--category", "-c", default=None)
@click.option("--deadline", "-dl", default=None)
@click.option("--priority", "-p",  default=None)
@click.option("--status", "-s", default=None)
@click.pass_context
def update(
        ctx,
        task_id: str,
        name: str,
        description: str,
        category: str,
        deadline: str,
        priority: str,
        status: str
) -> None:
    """
    Update a task by id.

    Find the task by id and update only those fields that correspond
    to the specified options. For example, to change only the name
    of the task, you need to use the following command:

        ''' tasks update -n "new_name" "id_value" '''

    To change the name and status of the task, you need to use the
    following command:

        ''' tasks update -n "new_name" -s "completed" "id_value" '''
    """

    task_service: TaskService = ctx.obj[TASK_SERVICE_NAME_IN_CLICK_CONTEXT]

    try:
        task_service.update(
            task_id,
            TaskUpdate(
                name=name,
                description=description,
                category=category,
                deadline=deadline,
                priority=priority,
                status=status
            )
        )

        click.echo(f"The task with id \"{task_id}\" has been successfully updated.")

    except TaskDoesNotExists as e:
        click.echo(e)

    except Exception as e:
        click.echo(f"Unknown error:\n{e}")

