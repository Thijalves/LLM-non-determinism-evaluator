import json
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

def load_results(filename: str):
    """Carrega resultados de um arquivo JSON."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo {filename} não encontrado!")
        return None
    except json.JSONDecodeError:
        print(f"❌ Erro ao decodificar JSON do arquivo {filename}")
        return None

def create_visualizations(results, output_prefix="visualization"):
    """Cria visualizações dos resultados."""
    
    # Extrair dados para visualização
    task_ids = []
    success_rates = []
    syntax_similarities = []
    ast_similarities = []
    non_determinism_scores = []
    
    # Verificar se é um arquivo de análise ou resultados brutos
    if isinstance(results, dict) and "task_analyses" in results:
        # É um arquivo de análise
        task_analyses = results.get("task_analyses", [])
        # Limitar para metade das tarefas
        half_size = len(task_analyses)
        task_analyses = task_analyses[:half_size]
        
        for task_result in task_analyses:
            task_id = task_result["task_id"]
            
            # Extrair dados da análise
            semantic = task_result["semantic_analysis"]
            summary = task_result["summary"]
            
            task_ids.append(task_id)
            success_rates.append(semantic["success_rate"])
            syntax_similarities.append(summary["avg_syntax_similarity"])
            ast_similarities.append(summary["avg_ast_similarity"])
            non_determinism_scores.append(summary["non_determinism_score"])
    else:
        # É um arquivo de resultados brutos
        results_list = [task for task in results if "analysis" in task]
        # Limitar para metade das tarefas
        half_size = len(results_list)
        results_list = results_list[:half_size]
        
        for task_result in results_list:
            task_id = task_result["task_id"]
            analysis = task_result["analysis"]
            
            task_ids.append(task_id)
            success_rates.append(analysis["semantic_analysis"]["success_rate"])
            syntax_similarities.append(analysis["summary"]["avg_syntax_similarity"])
            ast_similarities.append(analysis["summary"]["avg_ast_similarity"])
            non_determinism_scores.append(analysis["summary"]["non_determinism_score"])
    
    if not task_ids:
        print("❌ Nenhum dado de análise encontrado!")
        return
    
    print(f"📊 Gerando gráficos para {len(task_ids)} tarefas")
    
    # Converter nomes completos para siglas
    task_siglas = []
    for task_id in task_ids:
        # Extrair número da tarefa (ex: "HumanEval_0" -> "H0")
        if "HumanEval_" in task_id:
            number = task_id.split("_")[-1]
            task_siglas.append(f"H{number}")
        else:
            # Fallback para outros formatos
            task_siglas.append(task_id)
    
    # Configurar o estilo do matplotlib
    plt.style.use('default')
    
    # Criar pasta para salvar os gráficos
    os.makedirs("reports/visualizations", exist_ok=True)
    timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
    
    # 1. Taxa de Sucesso
    plt.figure(figsize=(12, 6))
    plt.bar(range(len(task_siglas)), success_rates, color='green', alpha=0.7)
    plt.title('Taxa de Sucesso por Tarefa (Metade do Dataset)', fontsize=14, fontweight='bold')
    plt.ylabel('Taxa de Sucesso', fontsize=12)
    plt.xlabel('Tarefas', fontsize=12)
    plt.ylim(0, 1)
    plt.xticks(range(len(task_siglas)), task_siglas, rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    filename = f"reports/visualizations/{output_prefix}_success_rate_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico de Taxa de Sucesso salvo em: {filename}")
    
    # 2. Similaridade Sintática
    plt.figure(figsize=(12, 6))
    plt.bar(range(len(task_siglas)), syntax_similarities, color='blue', alpha=0.7)
    plt.title('Similaridade Sintática Média por Tarefa (Metade do Dataset)', fontsize=14, fontweight='bold')
    plt.ylabel('Similaridade Sintática', fontsize=12)
    plt.xlabel('Tarefas', fontsize=12)
    plt.ylim(0, 1)
    plt.xticks(range(len(task_siglas)), task_siglas, rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    filename = f"reports/visualizations/{output_prefix}_syntax_similarity_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico de Similaridade Sintática salvo em: {filename}")
    
    # 3. Similaridade AST
    plt.figure(figsize=(12, 6))
    plt.bar(range(len(task_siglas)), ast_similarities, color='orange', alpha=0.7)
    plt.title('Similaridade Estrutural (AST) por Tarefa (Metade do Dataset)', fontsize=14, fontweight='bold')
    plt.ylabel('Similaridade AST', fontsize=12)
    plt.xlabel('Tarefas', fontsize=12)
    plt.ylim(0, 1)
    plt.xticks(range(len(task_siglas)), task_siglas, rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    filename = f"reports/visualizations/{output_prefix}_ast_similarity_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico de Similaridade AST salvo em: {filename}")
    
    # 4. Score de Não-Determinismo
    plt.figure(figsize=(12, 6))
    plt.bar(range(len(task_siglas)), non_determinism_scores, color='red', alpha=0.7)
    plt.title('Score de Não-Determinismo por Tarefa (Metade do Dataset)', fontsize=14, fontweight='bold')
    plt.ylabel('Score de Não-Determinismo', fontsize=12)
    plt.xlabel('Tarefas', fontsize=12)
    plt.ylim(0, 1)
    plt.xticks(range(len(task_siglas)), task_siglas, rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    filename = f"reports/visualizations/{output_prefix}_non_determinism_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico de Não-Determinismo salvo em: {filename}")
    
    # Mostrar estatísticas resumidas
    print(f"\n📈 ESTATÍSTICAS RESUMIDAS:")
    print(f"   • Taxa média de sucesso: {np.mean(success_rates):.2%}")
    print(f"   • Similaridade sintática média: {np.mean(syntax_similarities):.2%}")
    print(f"   • Similaridade AST média: {np.mean(ast_similarities):.2%}")
    print(f"   • Score médio de não-determinismo: {np.mean(non_determinism_scores):.2%}")
    
    # Análise de correlação
    if len(success_rates) > 1:  # Evitar erro com apenas um ponto
        print(f"\n🔍 ANÁLISE DE CORRELAÇÃO:")
        corr_success_syntax = np.corrcoef(success_rates, syntax_similarities)[0, 1]
        corr_success_ast = np.corrcoef(success_rates, ast_similarities)[0, 1]
        corr_success_non_det = np.corrcoef(success_rates, non_determinism_scores)[0, 1]
        
        print(f"   • Sucesso vs Sintática: {corr_success_syntax:.3f}")
        print(f"   • Sucesso vs AST: {corr_success_ast:.3f}")
        print(f"   • Sucesso vs Não-Determinismo: {corr_success_non_det:.3f}")

def create_comparison_matrix(results, output_prefix="comparison_matrix"):
    """Cria matriz de comparação para cada tarefa."""
    
    # Verificar se é um arquivo de análise ou resultados brutos
    if isinstance(results, dict) and "task_analyses" in results:
        # É um arquivo de análise
        task_analyses = results.get("task_analyses", [])
        # Limitar para metade das tarefas
        half_size = len(task_analyses)
        task_analyses = task_analyses[:half_size]
    else:
        # É um arquivo de resultados brutos
        task_analyses = [task for task in results if "analysis" in task]
        # Limitar para metade das tarefas
        half_size = len(task_analyses)
        task_analyses = task_analyses[:half_size]
    
    if not task_analyses:
        print("❌ Nenhum dado de análise encontrado!")
        return
    
    print(f"🔥 Gerando matrizes de comparação para {len(task_analyses)} tarefas (metade do total)")
    
    # Criar matriz de comparação para cada tarefa
    for task_analysis in task_analyses[:5]:  # Limitar a 5 tarefas para não sobrecarregar
        task_id = task_analysis["task_id"]
        
        # Verificar se há dados de comparação sintática
        if "syntax_comparisons" not in task_analysis:
            continue
            
        syntax_comparisons = task_analysis["syntax_comparisons"]
        if not syntax_comparisons:
            continue
        
        # Determinar número de soluções
        max_solution = max(max(comp["pair"]) for comp in syntax_comparisons)
        n_solutions = max_solution + 1
        
        # Criar matriz de similaridade
        matrix = np.zeros((n_solutions, n_solutions))
        for comp in syntax_comparisons:
            pair = comp["pair"]
            similarity = comp["syntax"]["similarity_ratio"]
            matrix[pair[0], pair[1]] = similarity
            matrix[pair[1], pair[0]] = similarity
        
        # Diagonal = 1 (auto-similaridade)
        np.fill_diagonal(matrix, 1.0)
        
        # Criar heatmap
        plt.figure(figsize=(8, 6))
        plt.imshow(matrix, cmap='RdYlBu_r', vmin=0, vmax=1)
        plt.colorbar(label='Similaridade Sintática')
        plt.title(f'Matriz de Similaridade - {task_id} (Metade do Dataset)')
        plt.xlabel('Solução')
        plt.ylabel('Solução')
        plt.xticks(range(n_solutions))
        plt.yticks(range(n_solutions))
        
        # Adicionar valores na matriz
        for i in range(n_solutions):
            for j in range(n_solutions):
                plt.text(j, i, f'{matrix[i, j]:.2f}', 
                        ha='center', va='center', color='black', fontsize=8)
        
        # Salvar heatmap
        os.makedirs("reports/visualizations", exist_ok=True)
        timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
        filename = f"reports/visualizations/{output_prefix}_{task_id}_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"🔥 Heatmap salvo em: {filename}")
        plt.close()

def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("❌ Uso: python3 visualize_results.py <arquivo_json>")
        print("   Exemplo: python3 visualize_results.py datasets/exp_1_llama3_164.json")
        print("   Ou: python3 visualize_results.py reports/analysis_exp_1_llama3_164.json")
        sys.exit(1)
    
    filename = sys.argv[1]
    print(f"📂 Carregando resultados de: {filename}")
    
    results = load_results(filename)
    if results is None:
        sys.exit(1)
    
    if isinstance(results, dict) and "task_analyses" in results:
        print(f"✅ Carregados dados de análise com {len(results.get('task_analyses', []))} tarefas")
    else:
        print(f"✅ Carregados {len(results)} tarefas")
    
    print("📊 Criando visualizações...")
    create_visualizations(results)
    create_comparison_matrix(results)
    print("✅ Visualizações concluídas!")

if __name__ == "__main__":
    main() 