#!/usr/bin/env python3
"""
Script para analisar erros do experimento 2 e gerar gráfico de barras.
"""

import json
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import Counter

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

def categorize_error(traceback: str) -> str:
    """Categoriza o tipo de erro baseado no traceback."""
    if not traceback:
        return "Sem erro"
    
    traceback_lower = traceback.lower()
    
    # Categorias de erro
    if "syntaxerror" in traceback_lower:
        return "SyntaxError"
    elif "nameerror" in traceback_lower:
        return "NameError"
    elif "typeerror" in traceback_lower:
        return "TypeError"
    elif "valueerror" in traceback_lower:
        return "ValueError"
    elif "attributeerror" in traceback_lower:
        return "AttributeError"
    elif "indentationerror" in traceback_lower:
        return "IndentationError"
    elif "importerror" in traceback_lower:
        return "ImportError"
    elif "timeout" in traceback_lower:
        return "Timeout"
    elif "assertion" in traceback_lower:
        return "AssertionError"
    elif "indexerror" in traceback_lower:
        return "IndexError"
    elif "keyerror" in traceback_lower:
        return "KeyError"
    elif "zerodivisionerror" in traceback_lower:
        return "ZeroDivisionError"
    elif "recursionerror" in traceback_lower:
        return "RecursionError"
    elif "memoryerror" in traceback_lower:
        return "MemoryError"
    elif "filenotfounderror" in traceback_lower:
        return "FileNotFoundError"
    elif "permissionerror" in traceback_lower:
        return "PermissionError"
    else:
        return "Outros"

def analyze_errors(results):
    """Analisa os erros nos resultados do experimento."""
    
    all_errors = []
    task_errors = {}
    error_categories = Counter()
    
    for task_result in results:
        task_id = task_result["task_id"]
        task_errors[task_id] = {
            "total_responses": 0,
            "passed": 0,
            "failed": 0,
            "timeout": 0,
            "error_types": Counter()
        }
        
        for response in task_result["responses"]:
            task_errors[task_id]["total_responses"] += 1
            
            test_result = response["test_result"]
            traceback = response.get("traceback", "")
            
            if test_result == "passed":
                task_errors[task_id]["passed"] += 1
            elif test_result == "timeout":
                task_errors[task_id]["timeout"] += 1
                task_errors[task_id]["error_types"]["Timeout"] += 1
                error_categories["Timeout"] += 1
            else:  # failed
                task_errors[task_id]["failed"] += 1
                
                # Categorizar erro
                error_type = categorize_error(traceback)
                task_errors[task_id]["error_types"][error_type] += 1
                error_categories[error_type] += 1
                all_errors.append({
                    "task_id": task_id,
                    "error_type": error_type,
                    "traceback": traceback
                })
    
    return {
        "all_errors": all_errors,
        "task_errors": task_errors,
        "error_categories": error_categories
    }

def create_error_visualizations(error_analysis, output_prefix="error_analysis"):
    """Cria visualizações dos erros."""
    
    error_categories = error_analysis["error_categories"]
    task_errors = error_analysis["task_errors"]
    
    # Criar pasta para salvar os gráficos
    os.makedirs("reports/visualizations", exist_ok=True)
    timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
    
    # 1. Gráfico de barras - Tipos de Erro + Soluções Corretas
    plt.figure(figsize=(14, 7))
    
    # Adicionar soluções corretas ao gráfico
    total_responses = sum(task_data["total_responses"] for task_data in task_errors.values())
    total_passed = sum(task_data["passed"] for task_data in task_errors.values())
    
    # Criar lista completa com soluções corretas e tipos de erro
    all_categories = ["Soluções Corretas"] + list(error_categories.keys())
    all_counts = [total_passed] + list(error_categories.values())
    
    # Cores baseadas no tipo
    colors = []
    for category in all_categories:
        if category == "Soluções Corretas":
            colors.append("green")
        elif category == "Timeout":
            colors.append("orange")
        elif category == "AssertionError":
            colors.append("red")
        elif category == "SyntaxError":
            colors.append("purple")
        elif category == "NameError":
            colors.append("blue")
        elif category == "TypeError":
            colors.append("darkgreen")
        else:
            colors.append("gray")
    
    bars = plt.bar(range(len(all_categories)), all_counts, color=colors, alpha=0.7)
    plt.title('Distribuição de Soluções Corretas e Tipos de Erro - Experimento 2', fontsize=14, fontweight='bold')
    plt.ylabel('Número de Ocorrências', fontsize=12)
    plt.xlabel('Categorias', fontsize=12)
    plt.xticks(range(len(all_categories)), all_categories, rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, count in zip(bars, all_counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(count), ha='center', va='bottom', fontweight='bold')
    
    # Adicionar porcentagens
    for i, (bar, count) in enumerate(zip(bars, all_counts)):
        percentage = (count / total_responses) * 100
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'({percentage:.1f}%)', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    filename = f"reports/visualizations/{output_prefix}_error_types_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico de Tipos de Erro + Soluções Corretas salvo em: {filename}")
    
    # 2. Gráfico de barras - Taxa de Erro por Tarefa
    task_ids = []
    error_rates = []
    success_rates = []
    
    for task_id, task_data in task_errors.items():
        task_ids.append(task_id)
        total = task_data["total_responses"]
        error_rate = (task_data["failed"] + task_data["timeout"]) / total if total > 0 else 0
        success_rate = task_data["passed"] / total if total > 0 else 0
        
        error_rates.append(error_rate)
        success_rates.append(success_rate)
    
    # Converter nomes para siglas
    task_siglas = []
    for task_id in task_ids:
        if "HumanEval_" in task_id:
            number = task_id.split("_")[-1]
            task_siglas.append(f"H{number}")
        else:
            task_siglas.append(task_id)
    
    # Limitar para metade das tarefas para melhor visualização
    half_size = len(task_siglas) // 2
    task_siglas = task_siglas[:half_size]
    error_rates = error_rates[:half_size]
    success_rates = success_rates[:half_size]
    
    plt.figure(figsize=(15, 6))
    x = np.arange(len(task_siglas))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, success_rates, width, label='Taxa de Sucesso', color='green', alpha=0.7)
    bars2 = plt.bar(x + width/2, error_rates, width, label='Taxa de Erro', color='red', alpha=0.7)
    
    plt.title('Taxa de Sucesso vs Erro por Tarefa - Experimento 2 (Metade)', fontsize=14, fontweight='bold')
    plt.ylabel('Taxa', fontsize=12)
    plt.xlabel('Tarefas', fontsize=12)
    plt.xticks(x, task_siglas, rotation=45)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.ylim(0, 1)
    
    # Adicionar valores nas barras
    for bar, rate in zip(bars1, success_rates):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{rate:.2f}', ha='center', va='bottom', fontsize=8)
    
    for bar, rate in zip(bars2, error_rates):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{rate:.2f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    filename = f"reports/visualizations/{output_prefix}_task_rates_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico de Taxas por Tarefa salvo em: {filename}")
    
    # 3. Gráfico de pizza - Distribuição Geral
    total_responses = sum(task_data["total_responses"] for task_data in task_errors.values())
    total_passed = sum(task_data["passed"] for task_data in task_errors.values())
    total_failed = sum(task_data["failed"] for task_data in task_errors.values())
    total_timeout = sum(task_data["timeout"] for task_data in task_errors.values())
    
    plt.figure(figsize=(10, 8))
    labels = ['Passou', 'Falhou', 'Timeout']
    sizes = [total_passed, total_failed, total_timeout]
    colors = ['green', 'red', 'orange']
    
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('Distribuição Geral de Resultados - Experimento 2', fontsize=14, fontweight='bold')
    plt.axis('equal')
    
    filename = f"reports/visualizations/{output_prefix}_pie_chart_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico de Pizza salvo em: {filename}")
    
    # Estatísticas resumidas
    print(f"\n📈 ESTATÍSTICAS DE ERROS - EXPERIMENTO 2:")
    print(f"   • Total de tarefas executadas: {len(task_errors)}")
    print(f"   • Total de experimentos (soluções): {total_responses}")
    print(f"   • Média de soluções por tarefa: {total_responses/len(task_errors):.1f}")
    print(f"   • Passaram: {total_passed} ({total_passed/total_responses:.2%})")
    print(f"   • Falharam: {total_failed} ({total_failed/total_responses:.2%})")
    print(f"   • Timeout: {total_timeout} ({total_timeout/total_responses:.2%})")
    print(f"   • Taxa de erro total: {(total_failed + total_timeout)/total_responses:.2%}")
    
    print(f"\n🔍 TOP 5 TIPOS DE ERRO:")
    for error_type, count in error_categories.most_common(5):
        print(f"   • {error_type}: {count} ocorrências")
    
    # Análise por tarefa
    tasks_with_all_passed = sum(1 for task_data in task_errors.values() if task_data["passed"] == task_data["total_responses"])
    tasks_with_all_failed = sum(1 for task_data in task_errors.values() if task_data["failed"] == task_data["total_responses"])
    tasks_mixed = len(task_errors) - tasks_with_all_passed - tasks_with_all_failed
    
    print(f"\n📊 ANÁLISE POR TAREFA:")
    print(f"   • Tarefas com todas as soluções passando: {tasks_with_all_passed}")
    print(f"   • Tarefas com todas as soluções falhando: {tasks_with_all_failed}")
    print(f"   • Tarefas com resultados mistos: {tasks_mixed}")
    print(f"   • Taxa de tarefas completamente bem-sucedidas: {tasks_with_all_passed/len(task_errors):.2%}")
    print(f"   • Taxa de tarefas completamente mal-sucedidas: {tasks_with_all_failed/len(task_errors):.2%}")

def main():
    """Função principal."""
    if len(sys.argv) != 2:
        print("❌ Uso: python3 analyze_errors.py <arquivo_resultados>")
        print("   Exemplo: python3 analyze_errors.py datasets/exp_2_llama3_164.json")
        sys.exit(1)
    
    filename = sys.argv[1]
    print(f"📂 Carregando resultados de: {filename}")
    
    results = load_results(filename)
    if not results:
        sys.exit(1)
    
    print(f"✅ Carregados dados com {len(results)} tarefas")
    
    # Analisar erros
    print("🔍 Analisando erros...")
    error_analysis = analyze_errors(results)
    
    # Criar visualizações
    print("📊 Criando visualizações...")
    create_error_visualizations(error_analysis)
    
    print("✅ Análise de erros concluída!")

if __name__ == "__main__":
    main() 