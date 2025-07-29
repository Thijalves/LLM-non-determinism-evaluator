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
    
    for task_result in results:
        if "analysis" in task_result:
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
    
    # Configurar o estilo do matplotlib
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análise de Não-Determinismo em Geração de Código', fontsize=16, fontweight='bold')
    
    # 1. Taxa de Sucesso
    axes[0, 0].bar(range(len(task_ids)), success_rates, color='green', alpha=0.7)
    axes[0, 0].set_title('Taxa de Sucesso por Tarefa')
    axes[0, 0].set_ylabel('Taxa de Sucesso')
    axes[0, 0].set_ylim(0, 1)
    axes[0, 0].set_xticks(range(len(task_ids)))
    axes[0, 0].set_xticklabels(task_ids, rotation=45)
    
    # 2. Similaridade Sintática
    axes[0, 1].bar(range(len(task_ids)), syntax_similarities, color='blue', alpha=0.7)
    axes[0, 1].set_title('Similaridade Sintática Média')
    axes[0, 1].set_ylabel('Similaridade Sintática')
    axes[0, 1].set_ylim(0, 1)
    axes[0, 1].set_xticks(range(len(task_ids)))
    axes[0, 1].set_xticklabels(task_ids, rotation=45)
    
    # 3. Similaridade AST
    axes[1, 0].bar(range(len(task_ids)), ast_similarities, color='orange', alpha=0.7)
    axes[1, 0].set_title('Similaridade Estrutural (AST)')
    axes[1, 0].set_ylabel('Similaridade AST')
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].set_xticks(range(len(task_ids)))
    axes[1, 0].set_xticklabels(task_ids, rotation=45)
    
    # 4. Score de Não-Determinismo
    axes[1, 1].bar(range(len(task_ids)), non_determinism_scores, color='red', alpha=0.7)
    axes[1, 1].set_title('Score de Não-Determinismo')
    axes[1, 1].set_ylabel('Score de Não-Determinismo')
    axes[1, 1].set_ylim(0, 1)
    axes[1, 1].set_xticks(range(len(task_ids)))
    axes[1, 1].set_xticklabels(task_ids, rotation=45)
    
    plt.tight_layout()
    
    # Salvar gráfico na pasta reports/visualizations
    os.makedirs("reports/visualizations", exist_ok=True)
    timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
    filename = f"reports/visualizations/{output_prefix}_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"📊 Gráfico salvo em: {filename}")
    
    # Mostrar estatísticas resumidas
    print(f"\n📈 ESTATÍSTICAS RESUMIDAS:")
    print(f"   • Taxa média de sucesso: {np.mean(success_rates):.2%}")
    print(f"   • Similaridade sintática média: {np.mean(syntax_similarities):.2%}")
    print(f"   • Similaridade AST média: {np.mean(ast_similarities):.2%}")
    print(f"   • Score médio de não-determinismo: {np.mean(non_determinism_scores):.2%}")
    
    # Análise de correlação
    if len(success_rates) > 1:  # Evitar erro com apenas um ponto
        print(f"\n🔍 ANÁLISE DE CORRELAÇÃO:")
        corr_syntax_success = np.corrcoef(syntax_similarities, success_rates)[0, 1]
        corr_ast_success = np.corrcoef(ast_similarities, success_rates)[0, 1]
        corr_syntax_ast = np.corrcoef(syntax_similarities, ast_similarities)[0, 1]
        
        print(f"   • Correlação sintaxe-sucesso: {corr_syntax_success:.3f}")
        print(f"   • Correlação AST-sucesso: {corr_ast_success:.3f}")
        print(f"   • Correlação sintaxe-AST: {corr_syntax_ast:.3f}")

def create_comparison_matrix(results, output_prefix="comparison_matrix"):
    """Cria uma matriz de comparação entre soluções."""
    
    for task_result in results:
        if "analysis" in task_result:
            task_id = task_result["task_id"]
            analysis = task_result["analysis"]
            syntax_comparisons = analysis["syntax_comparisons"]
            
            if syntax_comparisons:
                # Criar matriz de similaridade
                n_solutions = len(task_result["responses"])
                similarity_matrix = np.zeros((n_solutions, n_solutions))
                
                for comp in syntax_comparisons:
                    pair = comp["pair"]
                    similarity = comp["syntax"]["similarity_ratio"]
                    similarity_matrix[pair[0], pair[1]] = similarity
                    similarity_matrix[pair[1], pair[0]] = similarity
                
                # Diagonal = 1 (auto-similaridade)
                np.fill_diagonal(similarity_matrix, 1.0)
                
                # Criar heatmap
                plt.figure(figsize=(8, 6))
                plt.imshow(similarity_matrix, cmap='RdYlBu_r', vmin=0, vmax=1)
                plt.colorbar(label='Similaridade Sintática')
                plt.title(f'Matriz de Similaridade - {task_id}')
                plt.xlabel('Solução')
                plt.ylabel('Solução')
                plt.xticks(range(n_solutions))
                plt.yticks(range(n_solutions))
                
                # Adicionar valores na matriz
                for i in range(n_solutions):
                    for j in range(n_solutions):
                        plt.text(j, i, f'{similarity_matrix[i, j]:.2f}', 
                                ha='center', va='center', fontsize=10)
                
                # Salvar matriz na pasta reports/visualizations
                os.makedirs("reports/visualizations", exist_ok=True)
                timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
                filename = f"reports/visualizations/{output_prefix}_{task_id}_{timestamp}.png"
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                print(f"📊 Matriz de similaridade salva em: {filename}")
                plt.close()

def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("❌ Uso: python visualize_results.py <arquivo_resultados.json>")
        print("   Exemplo: python visualize_results.py datasets/exp_1_250728-200014.json")
        return
    
    filename = sys.argv[1]
    
    print(f"📂 Carregando resultados de: {filename}")
    results = load_results(filename)
    
    if not results:
        return
    
    print(f"✅ Carregados {len(results)} tarefas")
    
    # Criar visualizações
    print("📊 Criando visualizações...")
    create_visualizations(results)
    create_comparison_matrix(results)
    
    print("✅ Visualizações concluídas!")

if __name__ == "__main__":
    main() 