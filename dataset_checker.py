import traceback
from utils.dataset_handler import process_task, get_task
import random

def llama_mock(func):
    """
    Mock function to simulate the behavior of the Llama model.
    This is a placeholder and should be replaced with actual model logic.
    """
    if random.random() < 0.5:
        def wrong_solution(*args, **kwargs):
            return None
        return wrong_solution
    else:
        return func

dataset = "./datasets/human_eval.json"
for i in range(164):
    task_id = f"HumanEval_{i}"

    process_task(dataset, task_id, "./current_task")
    # task = get_task(dataset, task_id)

    # Imports
    from current_task.test_case import check
    from current_task.canonical_solution import canonical_solution

    try:
        check(llama_mock(canonical_solution))
    except AssertionError:
        tb_str = traceback.format_exc()
        print("Check failed:\n" + tb_str)
    else:
        print("Check passed")