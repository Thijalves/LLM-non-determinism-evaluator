from contextlib import contextmanager

from datetime import datetime
import json
import signal
import sys
import traceback
from typing import Literal

from utils.dataset_handler import get_entry_point, get_task, process_task
from utils.llm_handler import generate_code, save_solution
from utils.module_loader import load_module


class TimeoutException(Exception):
    pass

def generate_task_prompt(task: str, prompt_type: Literal['concise','chain_of_thought']):
    if prompt_type == 'concise':
        return f"Generate Python3 code (Markdown) for the following task, make the code as concise as possible:\n{task}"
    elif prompt_type == 'chain_of_thought':
        return f"Generate Chain-of-Thought steps of how to solve the problem first, and then generate Python3 code (Markdown):\n{task}"
    else:
        raise ValueError("Invalid prompt type. Use 'concise' or 'chain_of_thought'.")

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

total_tasks = 164
responses_per_task = 5


print(f"Starting evaluation of {total_tasks} tasks...")

for prompt_type in ('concise', 'chain_of_thought'):
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

        task = generate_task_prompt(task, prompt_type)

        task_results = {"task_id": task_id, "responses": []}

        for j in range(responses_per_task):
            print(f"  Generating {prompt_type} solution {j+1}/{responses_per_task} for {task_id}...")

            check = load_module("test", "./current_task/test.py").check

            try:
                code = generate_code(task, "llama3.2")
                save_solution(code, entry_point, "./current_task")
            
                generated_solution = load_module("generated_solution", "./current_task/generated_solution.py").generated_solution

                try:
                    with time_limit(timeout_seconds):
                        check(generated_solution)
                    test_result = "passed"
                    traceback_string = ""
                    print(f"    ✅ Passed test case.")
                except TimeoutException:
                    test_result = "timeout"
                    traceback_string = f"Function timed out after {timeout_seconds} seconds"
                    print(f"    ⏱️ Timeout after {timeout_seconds} seconds")
                except AssertionError:
                    # grab the full traceback as a list of lines
                    tb_lines = traceback.format_exc().splitlines()
                    # find the line that starts with 'assert'
                    traceback_string = next(
                        (line.strip() for line in tb_lines if line.strip().startswith("assert ")),
                        None
                    )
                    test_result = "failed"
                    print(f"    ❌ Assertion failed: {traceback_string}")
                except Exception:
                    # any other exception
                    print(f"    ❌ Error while running test:")
                    traceback_string = traceback.format_exc()
                    test_result = "failed"
                    print(f"    ❌ Error: {traceback_string.splitlines()[-1]}")
            except Exception:
                test_result = "failed"
                traceback_string = traceback.format_exc()
                print(f"❌ Error importing generated code: {traceback_string.splitlines()[-1]}")

            task_results["responses"].append({
                "code": code,
                "traceback": traceback_string,
                "test_result": test_result
            })

        
        results.append(task_results)
        print(f"✔ Finished {task_id}")

    # Save all results in a timestamped file
    timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
    filename = f"./datasets/exp_4_{prompt_type}_{timestamp}.json"
    print(f"\nSaving results to {filename}...")

    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

print("✅ All done!")


