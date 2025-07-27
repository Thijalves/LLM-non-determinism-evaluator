import traceback
from utils.dataset_handler import process_task, get_task, get_entry_point
from utils.llm_handler import generate_code, save_solution

dataset = "./datasets/human_eval.json"

for i in range(1): # set to 1 for test, should be 164
    task_id = f"HumanEval_{i}"

    # process and get task info
    process_task(dataset, task_id, "./current_task")
    task = get_task(dataset, task_id)
    entry_point = get_entry_point(dataset, task_id)

    code = generate_code(task, "llama3.2")
    save_solution(code, entry_point, "./current_task")
    from current_task.generated_solution import generated_solution
    
    # import test    
    from current_task.test_case import check

    try:
        check(generated_solution)
    except AssertionError:
        traceback_string = traceback.format_exc()
        print("Check failed:\n" + traceback_string)
    else:
        print("Check passed")