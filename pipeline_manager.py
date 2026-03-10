from error_guard import safe_execute
from task_registry import get_tasks


def run_pipeline(context=None):

    tasks = get_tasks()

    results = []

    for task in tasks:

        result = safe_execute(task, context)

        results.append(result)

    return results
