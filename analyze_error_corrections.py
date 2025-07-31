#!/usr/bin/env python3
"""
Script para analisar a correção de erros entre experimentos.
"""

import json
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import Counter, defaultdict

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

def analyze_error_corrections(exp1_results, exp2_results):
    """Analisa como os erros foram corrigidos entre experimentos."""
    
    # Analisar erros do experimento 1
    exp1_errors = defaultdict(int)
    exp1_task_errors = {}
    
    for task_result in exp1_results:
        task_id = task_result["task_id"]
        exp1_task_errors[task_id] = {
            "passed": 0,
            "failed": 0,
            "timeout": 0,
            "error_types": Counter()
        }
        
        for response in task_result["responses"]:
            test_result = response["test_result"]
            traceback = response.get("traceback", "")
            
            if test_result == "passed":
                exp1_task_errors[task_id]["passed"] += 1
            elif test_result == "timeout":
                exp1_task_errors[task_id]["timeout"] += 1
                exp1_task_errors[task_id]["error_types"]["Timeout"] += 1
                exp1_errors["Timeout"] += 1
            else:  # failed
                exp1_task_errors[task_id]["failed"] += 1
                error_type = categorize_error(traceback)
                exp1_task_errors[task_id]["error_types"][error_type] += 1
                exp1_errors[error_type] += 1
    
    # Analisar erros do experimento 2
    exp2_errors = defaultdict(int)
    exp2_task_errors = {}
    
    for task_result in exp2_results:
        task_id = task_result["task_id"]
        exp2_task_errors[task_id] = {
            "passed": 0,
            "failed": 0,
            "timeout": 0,
            "error_types": Counter()
        }
        
        for response in task_result["responses"]:
            test_result = response["test_result"]
            traceback = response.get("traceback", "")
            
            if test_result == "passed":
                exp2_task_errors[task_id]["passed"] += 1
            elif test_result == "timeout":
                exp2_task_errors[task_id]["timeout"] += 1
                exp2_task_errors[task_id]["error_types"]["Timeout"] += 1
                exp2_errors["Timeout"] += 1
            else:  # failed
                exp2_task_errors[task_id]["failed"] += 1
                error_type = categorize_error(traceback)
                exp2_task_errors[task_id]["error_types"][error_type] += 1
                exp2_errors[error_type] += 1
    
    # Calcular melhorias por tipo de erro
    error_improvements = {}
    all_error_types = set(exp1_errors.keys()) | set(exp2_errors.keys())
    
    for error_type in all_error_types:
        exp1_count = exp1_errors.get(error_type, 0)
        exp2_count = exp2_errors.get(error_type, 0)
        
        if exp1_count > 0:
            improvement = exp1_count - exp2_count
            improvement_percentage = (improvement / exp1_count) * 100
        else:
            improvement = 0
            improvement_percentage = 0
        
        error_improvements[error_type] = {
            "exp1_count": exp1_count,
            "exp2_count": exp2_count,
            "improvement": improvement,
            "improvement_percentage": improvement_percentage
        }
    
    return {
        "exp1_errors": exp1_errors,
        "exp2_errors": exp2_errors,
        "error_improvements": error_improvements,
        "exp1_task_errors": exp1_task_errors,
        "exp2_task_errors": exp2_task_errors
    }

def create_correction_visualizations(analysis, output_prefix="error_corrections"):
    """Cria visualizações das correções de erro."""
    
    error_improvements = analysis["error_improvements"]
    exp1_errors = analysis["exp1_errors"]
    exp2_errors = analysis["exp2_errors"]
    
    # Criar pasta para salvar os gráficos
    os.makedirs("reports/visualizations", exist_ok=True)
    timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
    
    # 1. Gráfico de barras - Comparação de Erros entre Experimentos
    plt.figure(figsize=(16, 8))
    
    # Filtrar apenas tipos de erro que apareceram em pelo menos um experimento
    error_types = [error_type for error_type in error_improvements.keys() 
                   if error_improvements[error_type]["exp1_count"] > 0 or 
                   error_improvements[error_type]["exp2_count"] > 0]
    
    exp1_counts = [error_improvements[error_type]["exp1_count"] for error_type in error_types]
    exp2_counts = [error_improvements[error_type]["exp2_count"] for error_type in error_types]
    
    x = np.arange(len(error_types))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, exp1_counts, width, label='Experimento 1', color='red', alpha=0.7)
    bars2 = plt.bar(x + width/2, exp2_counts, width, label='Experimento 2', color='blue', alpha=0.7)
    
    plt.title('Comparação de Tipos de Erro entre Experimentos', fontsize=14, fontweight='bold')
    plt.ylabel('Número de Erros', fontsize=12)
    plt.xlabel('Tipos de Erro', fontsize=12)
    plt.xticks(x, error_types, rotation=45)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, count in zip(bars1, exp1_counts):
        if count > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', va='bottom', fontweight='bold')
    
    for bar, count in zip(bars2, exp2_counts):
        if count > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    filename = f"reports/visualizations/{output_prefix}_comparison_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico de Comparação salvo em: {filename}")
    
    # 2. Gráfico de barras - Melhorias por Tipo de Erro
    plt.figure(figsize=(14, 7))
    
    # Filtrar apenas erros que melhoraram
    improved_errors = [(error_type, data) for error_type, data in error_improvements.items() 
                       if data["improvement"] > 0 and data["exp1_count"] > 0]
    improved_errors.sort(key=lambda x: x[1]["improvement_percentage"], reverse=True)
    
    if improved_errors:
        error_types_improved = [item[0] for item in improved_errors]
        improvements = [item[1]["improvement_percentage"] for item in improved_errors]
        
        colors = []
        for error_type in error_types_improved:
            if error_type == "TypeError":
                colors.append("darkgreen")
            elif error_type == "NameError":
                colors.append("blue")
            elif error_type == "Timeout":
                colors.append("orange")
            else:
                colors.append("green")
        
        bars = plt.bar(range(len(error_types_improved)), improvements, color=colors, alpha=0.7)
        plt.title('Melhorias por Tipo de Erro (Experimento 1 → 2)', fontsize=14, fontweight='bold')
        plt.ylabel('Melhoria (%)', fontsize=12)
        plt.xlabel('Tipos de Erro', fontsize=12)
        plt.xticks(range(len(error_types_improved)), error_types_improved, rotation=45)
        plt.grid(axis='y', alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, improvement in zip(bars, improvements):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{improvement:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        filename = f"reports/visualizations/{output_prefix}_improvements_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📊 Gráfico de Melhorias salvo em: {filename}")
    
    # 3. Gráfico de pizza - Distribuição de Melhorias
    plt.figure(figsize=(10, 8))
    
    # Calcular totais
    total_exp1_errors = sum(exp1_errors.values())
    total_exp2_errors = sum(exp2_errors.values())
    total_improvement = total_exp1_errors - total_exp2_errors
    
    labels = ['Erros Corrigidos', 'Erros Restantes']
    sizes = [total_improvement, total_exp2_errors]
    colors = ['green', 'red']
    
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('Distribuição Geral de Correções de Erro', fontsize=14, fontweight='bold')
    plt.axis('equal')
    
    filename = f"reports/visualizations/{output_prefix}_pie_chart_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Gráfico de Pizza salvo em: {filename}")
    
    # Estatísticas resumidas
    print(f"\n📈 ESTATÍSTICAS DE CORREÇÃO DE ERROS:")
    print(f"   • Total de erros no Experimento 1: {total_exp1_errors}")
    print(f"   • Total de erros no Experimento 2: {total_exp2_errors}")
    print(f"   • Total de erros corrigidos: {total_improvement}")
    print(f"   • Taxa de correção geral: {(total_improvement/total_exp1_errors)*100:.1f}%")
    
    print(f"\n🔍 TOP 5 MELHORIAS POR TIPO DE ERRO:")
    for error_type, data in sorted(improved_errors, key=lambda x: x[1]["improvement_percentage"], reverse=True)[:5]:
        print(f"   • {error_type}: {data['improvement']} erros corrigidos ({data['improvement_percentage']:.1f}%)")
    
    # Análise de pioras
    worsened_errors = [(error_type, data) for error_type, data in error_improvements.items() 
                       if data["improvement"] < 0]
    
    if worsened_errors:
        print(f"\n⚠️ TIPOS DE ERRO QUE PIORARAM:")
        for error_type, data in worsened_errors:
            print(f"   • {error_type}: {abs(data['improvement'])} erros a mais ({abs(data['improvement_percentage']):.1f}%)")

def main():
    """Função principal."""
    if len(sys.argv) != 3:
        print("❌ Uso: python3 analyze_error_corrections.py <exp1_file> <exp2_file>")
        print("   Exemplo: python3 analyze_error_corrections.py datasets/exp_1_llama3_164.json datasets/exp_2_llama3_164.json")
        sys.exit(1)
    
    exp1_file = sys.argv[1]
    exp2_file = sys.argv[2]
    
    print(f"📂 Carregando Experimento 1: {exp1_file}")
    exp1_results = load_results(exp1_file)
    if not exp1_results:
        sys.exit(1)
    
    print(f"📂 Carregando Experimento 2: {exp2_file}")
    exp2_results = load_results(exp2_file)
    if not exp2_results:
        sys.exit(1)
    
    print(f"✅ Carregados dados: {len(exp1_results)} tarefas (Exp1) e {len(exp2_results)} tarefas (Exp2)")
    
    # Analisar correções
    print("🔍 Analisando correções de erro...")
    analysis = analyze_error_corrections(exp1_results, exp2_results)
    
    # Criar visualizações
    print("📊 Criando visualizações...")
    create_correction_visualizations(analysis)
    
    print("✅ Análise de correções concluída!")

if __name__ == "__main__":
    main() 