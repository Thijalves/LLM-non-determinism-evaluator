import json
import traceback
from datetime import datetime
from utils.dataset_handler import process_task, get_task, get_entry_point
from utils.llm_handler import generate_code, save_solution

dataset = "./datasets/human_eval.json"
results = []

for i in range(1):  # Change to 164 for full run
    task_id = f"HumanEval_{i}"
    process_task(dataset, task_id, "./current_task")
    task = get_task(dataset, task_id)
    entry_point = get_entry_point(dataset, task_id)

    task_results = {
        "task_id": task_id,
        "responses": []
    }

    for j in range(5):  # Generate 5 solutions
        code = generate_code(task, "llama3.2")
        save_solution(code, entry_point, "./current_task")

        try:
            from current_task.generated_solution import generated_solution
            from current_task.test_case import check
            check(generated_solution)
            test_result = "passed"
            traceback_string = ""
        except Exception:
            test_result = "failed"
            traceback_string = traceback.format_exc()

        task_results["responses"].append({
            "code": code,
            "traceback": traceback_string,
            "test_result": test_result
        })

    results.append(task_results)

# Save all results in a timestamped file
timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
filename = f"./datasets/exp_1_{timestamp}.json"

with open(filename, "w") as f:
    json.dump(results, f, indent=2)