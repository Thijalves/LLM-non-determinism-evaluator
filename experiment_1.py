import json
import sys
import traceback
from datetime import datetime
from utils.module_loader import load_module
from utils.dataset_handler import process_task, get_task, get_entry_point
from utils.llm_handler import generate_code, save_solution
from utils.analysis import compare_solutions, generate_analysis_report
import signal
from contextlib import contextmanager
import os

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

total_tasks = 164  # Change to 164 for full run
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

        try:
            code = generate_code(task, "llama3.2")
            save_solution(code, entry_point, "./current_task")
        
            # Load generated code
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

    # Automatic analysis of solutions for this task
    if len(task_results["responses"]) > 1:
        print(f"  🔬 Analyzing similarity between {len(task_results['responses'])} solutions...")
        analysis = compare_solutions(task_results["responses"])
        
        # Add analysis to results
        task_results["analysis"] = analysis
        
        # Print analysis summary
        summary = analysis["summary"]
        semantic = analysis["semantic_analysis"]
        
        print(f"    📊 Análise para {task_id}:")
        print(f"      • Taxa de sucesso: {semantic['success_rate']:.2%}")
        print(f"      • Similaridade sintática média: {summary['avg_syntax_similarity']:.2%}")
        print(f"      • Similaridade AST média: {summary['avg_ast_similarity']:.2%}")
        print(f"      • Score de não-determinismo: {summary['non_determinism_score']:.2%}")
        print(f"      • Consistência semântica: {'✅' if semantic['semantic_consistency'] else '❌'}")

    results.append(task_results)
    print(f"✔ Finished {task_id}")

# Save all results in a timestamped file
timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
filename = f"./datasets/exp_1_{timestamp}.json"
print(f"\nSaving results to {filename}...")

with open(filename, "w") as f:
    json.dump(results, f, indent=2)

print("✅ All done!")

# Generate complete analysis report
print("\n🔬 Generating complete analysis report...")
analysis_report = generate_analysis_report(results)

# Save analysis report in reports/analysis folder
os.makedirs("reports/analysis", exist_ok=True)
analysis_filename = f"./reports/analysis/analysis_report_{timestamp}.json"
with open(analysis_filename, "w") as f:
    json.dump(analysis_report, f, indent=2)

print(f"📊 Relatório de análise salvo em: {analysis_filename}")

# Print final summary
if analysis_report.get("aggregate_stats"):
    stats = analysis_report["aggregate_stats"]
    print(f"\n📈 FINAL SUMMARY:")
    print(f"   • Total de tarefas analisadas: {stats['total_tasks']}")
    print(f"   • Taxa média de sucesso: {stats['avg_success_rate']:.2%}")
    print(f"   • Score médio de não-determinismo: {stats['avg_non_determinism_score']:.2%}")
    print(f"   • Tarefas semanticamente consistentes: {stats['semantically_consistent_tasks']}")
    print(f"   • Tarefas semanticamente inconsistentes: {stats['semantically_inconsistent_tasks']}")