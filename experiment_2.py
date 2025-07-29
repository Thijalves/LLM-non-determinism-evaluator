import json
import sys
import traceback
from datetime import datetime
from utils.module_loader import load_module
from utils.dataset_handler import process_task, get_task, get_entry_point
from utils.llm_handler import generate_code, save_solution
import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

dataset = "./datasets/human_eval.json"
results = []
timeout_seconds = 5
max_attempts = 5
total_tasks = 164 
responses_per_task = 5

print(f"Starting evaluation of {total_tasks} tasks...")

for i in range(total_tasks):
    task_id = f"HumanEval_{i}"
    print(f"\nProcessing {task_id}:")

    process_task(dataset, task_id, "./current_task")

    try:
        task = get_task(dataset, task_id)
        entry_point = get_entry_point(dataset, task_id)
    except Exception:
        print(f"❌ Error while loading task or entry point for {task_id}:")
        print(traceback.format_exc())
        sys.exit(1)

    task_results = {
        "task_id": task_id,
        "responses": []
    }

    for j in range(responses_per_task):
        print(f"  Generating solution {j+1}/{responses_per_task} for {task_id}...")
        
        # Load generated test
        check = load_module("test", "./current_task/test.py").check
        
        feedback = None
        attempts = 0
        test_result = "failed"
        traceback_string = ""
        code = ""
        
        while attempts < max_attempts and test_result != "passed":
            attempts += 1
            print(f"    Attempt {attempts}/{max_attempts}")
            
            try:
                # Generate code with feedback from previous attempt if available
                code = generate_code(task, "llama3.2", feedback=feedback)
                save_solution(code, entry_point, "./current_task")
            
                previous_code = code

                # Load generated code
                generated_solution = load_module("generated_solution", "./current_task/generated_solution.py").generated_solution
            except Exception:
                traceback_string = traceback.format_exc()
                print(f"❌ error importing generated code {traceback_string.splitlines()[-1]}")
                feedback = {
                    'error': f"Code failed to compile/import with error: {traceback_string.splitlines()[-1]}",
                    'previous_code': previous_code
                }
                continue
            
            try:
                with time_limit(timeout_seconds):
                    check(generated_solution)
                test_result = "passed"
                traceback_string = ""
                print(f"    ✅ Passed test case.")
                break  # Success, exit the retry loop
            except TimeoutException:
                test_result = "timeout"
                traceback_string = f"Function timed out after {timeout_seconds} seconds"
                feedback = f"The code timed out after {timeout_seconds} seconds. Please optimize for performance."
                print(f"    ⏱️ Timeout after {timeout_seconds} seconds")
            except AssertionError:
                tb_lines = traceback.format_exc().splitlines()
                traceback_string = next(
                    (line.strip() for line in tb_lines if line.strip().startswith("assert ")),
                    None
                )
                test_result = "failed"
                feedback = f"The code failed an assertion: {traceback_string}. Please fix the implementation."
                print(f"    ❌ Assertion failed: {traceback_string}")
            except Exception:
                traceback_string = traceback.format_exc()
                test_result = "failed"
                feedback = f"The code raised an exception: {traceback_string.splitlines()[-1]}. Please fix the implementation."
                print(f"    ❌ Error while running test: {traceback_string.splitlines()[-1]}")

        task_results["responses"].append({
            "code": code,
            "traceback": traceback_string,
            "test_result": test_result,
            "attempts": attempts
        })

    results.append(task_results)
    print(f"✔ Finished {task_id}")

# Save all results in a timestamped file
timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
filename = f"./datasets/exp_2_{timestamp}.json"
print(f"\nSaving results to {filename}...")

with open(filename, "w") as f:
    json.dump(results, f, indent=2)

print("✅ All done!")