import json
import sys
from datetime import datetime
from utils.analysis import generate_analysis_report
import os

def load_results(filename: str):
    # Load the results from the file
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo {filename} não encontrado!")
        return None
    except json.JSONDecodeError:
        print(f"❌ Erro ao decodificar JSON do arquivo {filename}")
        return None

def print_analysis_report(report: dict):
    # Print the report header
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE ANÁLISE DE NÃO-DETERMINISMO")
    print("="*60)
    
    stats = report.get("aggregate_stats", {})
    if stats:
        print(f"\n📈 ESTATÍSTICAS GERAIS:")
        print(f"   • Total de tarefas analisadas: {stats.get('total_tasks', 0)}")
        print(f"   • Taxa média de sucesso: {stats.get('avg_success_rate', 0):.2%}")
        print(f"   • Score médio de não-determinismo: {stats.get('avg_non_determinism_score', 0):.2%}")
        print(f"   • Tarefas semanticamente consistentes: {stats.get('semantically_consistent_tasks', 0)}")
        print(f"   • Tarefas semanticamente inconsistentes: {stats.get('semantically_inconsistent_tasks', 0)}")
    
    # Analyze task by task
    task_analyses = report.get("task_analyses", [])
    if task_analyses:
        print(f"\n🔍 ANÁLISE POR TAREFA:")
        for analysis in task_analyses:
            task_id = analysis.get("task_id", "Unknown")
            summary = analysis.get("summary", {})
            semantic = analysis.get("semantic_analysis", {})
            
            print(f"\n   📋 {task_id}:")
            print(f"      • Taxa de sucesso: {semantic.get('success_rate', 0):.2%}")
            print(f"      • Similaridade sintática média: {summary.get('avg_syntax_similarity', 0):.2%}")
            print(f"      • Similaridade AST média: {summary.get('avg_ast_similarity', 0):.2%}")
            print(f"      • Score de não-determinismo: {summary.get('non_determinism_score', 0):.2%}")
            print(f"      • Consistência semântica: {'✅' if semantic.get('semantic_consistency', False) else '❌'}")
            
            syntax_comparisons = analysis.get("syntax_comparisons", [])
            if syntax_comparisons:
                print(f"      • Comparações sintáticas:")
                for comp in syntax_comparisons[:3]: 
                    pair = comp.get("pair", (0, 0))
                    syntax = comp.get("syntax", {})
                    print(f"        - Par {pair[0]}-{pair[1]}: {syntax.get('similarity_ratio', 0):.2%} similaridade")

def analyze_specific_task(report: dict, task_id: str):
    # Analyze a specific task in detail
    task_analyses = report.get("task_analyses", [])
    
    for analysis in task_analyses:
        if analysis.get("task_id") == task_id:
            print(f"\n🔬 ANÁLISE DETALHADA PARA {task_id}")
            print("="*50)
            
            semantic = analysis.get("semantic_analysis", {})
            summary = analysis.get("summary", {})
            
            print(f"📊 Resumo:")
            print(f"   • Total de soluções: {summary.get('total_solutions', 0)}")
            print(f"   • Taxa de sucesso: {semantic.get('success_rate', 0):.2%}")
            print(f"   • Passaram: {semantic.get('passed_count', 0)}")
            print(f"   • Falharam: {semantic.get('failed_count', 0)}")
            print(f"   • Score de não-determinismo: {summary.get('non_determinism_score', 0):.2%}")
            
            syntax_comparisons = analysis.get("syntax_comparisons", [])
            if syntax_comparisons:
                print(f"\n🔍 Comparações Sintáticas:")
                for i, comp in enumerate(syntax_comparisons):
                    pair = comp.get("pair", (0, 0))
                    syntax = comp.get("syntax", {})
                    ast_analysis = comp.get("ast", {})
                    
                    print(f"   📋 Par {pair[0]}-{pair[1]}:")
                    print(f"      • Similaridade sintática: {syntax.get('similarity_ratio', 0):.2%}")
                    print(f"      • Similaridade de tokens: {syntax.get('token_similarity', 0):.2%}")
                    print(f"      • Similaridade estrutural (AST): {ast_analysis.get('structure_similarity', 0):.2%}")
                    print(f"      • Match exato: {'✅' if syntax.get('exact_match', False) else '❌'}")
            
            return
    
    print(f"❌ Tarefa {task_id} não encontrada no relatório!")

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python analyze_results.py <results_file.json> [task_id]")
        print("   Example: python analyze_results.py datasets/exp_1_250728-200014.json")
        print("   Exemplo: python analyze_results.py datasets/exp_1_250728-200014.json HumanEval_0")
        return
    
    filename = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"📂 Carregando resultados de: {filename}")
    results = load_results(filename)
    
    if not results:
        return
    
    print(f"✅ Carregados {len(results)} tarefas")
    
    print("🔬 Gerando análise...")
    report = generate_analysis_report(results)
    print_analysis_report(report)
    
    os.makedirs("reports/", exist_ok=True)
    base_filename = os.path.basename(filename)
    report_filename = f"reports/analysis_{base_filename}"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {report_filename}")
    
    if task_id:
        analyze_specific_task(report, task_id)

if __name__ == "__main__":
    main() 