import json
import traceback
from datetime import datetime
from utils.module_loader import load_module
from utils.dataset_handler import process_task, get_task, get_entry_point
from utils.llm_handler import generate_code, save_solution

dataset = "./datasets/human_eval.json"
results = []

total_tasks = 1  # Change to 164 for full run
responses_per_task = 5

print(f"Starting evaluation of {total_tasks} tasks...")

for i in range(total_tasks):
    task_id = f"HumanEval_{i}"
    print(f"\nProcessing {task_id}:")

    process_task(dataset, task_id, "./current_task")
    task = get_task(dataset, task_id)
    entry_point = get_entry_point(dataset, task_id)

    task_results = {
        "task_id": task_id,
        "responses": []
    }

    for j in range(responses_per_task):
        print(f"  Generating solution {j+1}/{responses_per_task} for {task_id}...")

        code = generate_code(task, "llama3.2")
        save_solution(code, entry_point, "./current_task")

        # Load generated code and test
        check = load_module("test", "./current_task/test.py").check
        generated_solution = load_module("generated_solution", "./current_task/generated_solution.py").generated_solution

        try:
            
            check(generated_solution)
            test_result = "passed"
            traceback_string = ""
            print(f"    ✅ Passed test case.")
        except Exception:
            test_result = "failed"
            traceback_string = traceback.format_exc()
            print(f"    ❌ Failed test case:\n{traceback_string.splitlines()[-1]}")

        task_results["responses"].append({
            "code": code,
            "traceback": traceback_string,
            "test_result": test_result
        })

    results.append(task_results)
    print(f"✔ Finished {task_id}")

# Save all results in a timestamped file
timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
filename = f"./datasets/exp_1_{timestamp}.json"
print(f"\nSaving results to {filename}...")

with open(filename, "w") as f:
    json.dump(results, f, indent=2)

print("✅ All done!")