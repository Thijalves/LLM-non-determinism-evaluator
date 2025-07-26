import traceback
from utils.dataset_handler import process_task, get_task
from utils.llm_handler import generate_solution

dataset = "./datasets/human_eval.json"

for i in range(1): # set to 1 for test, should be 164
    task_id = f"HumanEval_{i}"

    # process and get task info
    process_task(dataset, task_id, "./current_task")
    task = get_task(dataset, task_id)

    generate_solution(task, "llama3.2", './current_task')
