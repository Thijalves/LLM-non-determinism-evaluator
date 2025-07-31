#!/usr/bin/env python3
"""
Análise específica para o Experimento 3 - Variação de Parâmetros
"""

import json
import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime

def load_experiment_3_data(filename):
    """Carrega dados do Experimento 3"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"❌ Erro ao carregar {filename}: {e}")
        return None

def analyze_parameter_impact(data):
    """Analisa o impacto dos diferentes parâmetros"""
    results = []
    
    for task in data:
        task_id = task['task_id']
        for response in task['responses']:
            results.append({
                'task_id': task_id,
                'config_name': response['config_name'],
                'temperature': response['model_params']['temperature'],
                'top_p': response['model_params']['top_p'],
                'top_k': response['model_params']['top_k'],
                'num_predict': response['model_params']['num_predict'],
                'test_result': response['test_result'],
                'code_length': len(response['code']),
                'passed': 1 if response['test_result'] == 'passed' else 0
            })
    
    df = pd.DataFrame(results)
    return df

def generate_comparison_report(df):
    """Gera relatório de comparação entre configurações"""
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE ANÁLISE - EXPERIMENTO 3")
    print("="*60)
    
    # Estatísticas gerais
    total_responses = len(df)
    overall_success_rate = df['passed'].mean() * 100
    
    print(f"\n📈 Estatísticas Gerais:")
    print(f"Total de respostas: {total_responses}")
    print(f"Taxa de sucesso geral: {overall_success_rate:.1f}%")
    
    # Por configuração
    print(f"\n🎯 Desempenho por Configuração:")
    config_stats = df.groupby('config_name').agg({
        'passed': ['count', 'sum', 'mean'],
        'code_length': ['mean', 'std'],
        'temperature': 'first',
        'top_p': 'first',
        'top_k': 'first'
    }).round(3)
    
    for config in df['config_name'].unique():
        config_data = df[df['config_name'] == config]
        success_rate = config_data['passed'].mean() * 100
        total_tasks = len(config_data)
        passed_tasks = config_data['passed'].sum()
        avg_code_length = config_data['code_length'].mean()
        temp = config_data['temperature'].iloc[0]
        
        print(f"\n  {config}:")
        print(f"    Taxa de sucesso: {success_rate:.1f}% ({passed_tasks}/{total_tasks})")
        print(f"    Comprimento médio do código: {avg_code_length:.0f} chars")
        print(f"    Temperature: {temp}")
    
    # Correlações
    print(f"\n🔗 Correlações com Taxa de Sucesso:")
    correlations = df[['temperature', 'top_p', 'top_k', 'num_predict', 'passed']].corr()['passed'].sort_values(ascending=False)
    
    for param, corr in correlations.items():
        if param != 'passed':
            direction = "positiva" if corr > 0 else "negativa"
            strength = "forte" if abs(corr) > 0.3 else "moderada" if abs(corr) > 0.1 else "fraca"
            print(f"    {param}: {corr:.3f} (correlação {strength} {direction})")
    
    return config_stats

def create_visualizations(df, output_dir):
    """Cria visualizações dos resultados"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Taxa de sucesso por configuração
    plt.figure(figsize=(12, 6))
    config_success = df.groupby('config_name')['passed'].mean() * 100
    colors = ['#2E8B57', '#4169E1', '#FF6347', '#FFD700', '#9370DB']
    
    bars = plt.bar(config_success.index, config_success.values, color=colors, alpha=0.7)
    plt.title('Taxa de Sucesso por Configuração de Parâmetros', fontsize=14, fontweight='bold')
    plt.ylabel('Taxa de Sucesso (%)')
    plt.xlabel('Configuração')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, config_success.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/success_rate_by_config.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Scatter plot: Temperature vs Success Rate
    plt.figure(figsize=(10, 6))
    temp_success = df.groupby('temperature')['passed'].mean() * 100
    temps = df.groupby('temperature')['config_name'].first()
    
    scatter = plt.scatter(temp_success.index, temp_success.values, 
                         c=range(len(temp_success)), cmap='viridis', s=100, alpha=0.7)
    
    for temp, success, config in zip(temp_success.index, temp_success.values, temps.values):
        plt.annotate(config, (temp, success), xytext=(5, 5), 
                    textcoords='offset points', fontsize=9)
    
    plt.title('Relação entre Temperature e Taxa de Sucesso', fontsize=14, fontweight='bold')
    plt.xlabel('Temperature')
    plt.ylabel('Taxa de Sucesso (%)')
    plt.grid(True, alpha=0.3)
    
    # Linha de tendência
    z = np.polyfit(temp_success.index, temp_success.values, 1)
    p = np.poly1d(z)
    plt.plot(temp_success.index, p(temp_success.index), "r--", alpha=0.8, linewidth=2)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/temperature_vs_success.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Comprimento do código por configuração
    plt.figure(figsize=(12, 6))
    df.boxplot(column='code_length', by='config_name', ax=plt.gca())
    plt.title('Distribuição do Comprimento do Código por Configuração')
    plt.suptitle('')  # Remove o título automático do pandas
    plt.ylabel('Comprimento do Código (caracteres)')
    plt.xlabel('Configuração')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/code_length_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Visualizações salvas em: {output_dir}/")

def generate_detailed_analysis(data, output_filename):
    """Gera análise detalhada em JSON"""
    df = analyze_parameter_impact(data)
    
    analysis = {
        "experiment_type": "parameter_variation",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tasks": len(data),
            "total_responses": len(df),
            "configurations_tested": df['config_name'].nunique(),
            "overall_success_rate": float(df['passed'].mean()),
        },
        "configuration_performance": {},
        "parameter_correlations": {},
        "insights": []
    }
    
    # Performance por configuração
    for config in df['config_name'].unique():
        config_data = df[df['config_name'] == config]
        analysis["configuration_performance"][config] = {
            "success_rate": float(config_data['passed'].mean()),
            "total_attempts": len(config_data),
            "successful_attempts": int(config_data['passed'].sum()),
            "avg_code_length": float(config_data['code_length'].mean()),
            "parameters": {
                "temperature": float(config_data['temperature'].iloc[0]),
                "top_p": float(config_data['top_p'].iloc[0]),
                "top_k": int(config_data['top_k'].iloc[0]),
                "num_predict": int(config_data['num_predict'].iloc[0])
            }
        }
    
    # Correlações
    correlations = df[['temperature', 'top_p', 'top_k', 'num_predict', 'passed']].corr()['passed']
    for param, corr in correlations.items():
        if param != 'passed':
            analysis["parameter_correlations"][param] = float(corr)
    
    # Insights automáticos
    best_config = max(analysis["configuration_performance"].items(), 
                     key=lambda x: x[1]["success_rate"])
    worst_config = min(analysis["configuration_performance"].items(), 
                      key=lambda x: x[1]["success_rate"])
    
    analysis["insights"].extend([
        f"Melhor configuração: {best_config[0]} ({best_config[1]['success_rate']:.1%} de sucesso)",
        f"Pior configuração: {worst_config[0]} ({worst_config[1]['success_rate']:.1%} de sucesso)",
        f"Diferença de performance: {(best_config[1]['success_rate'] - worst_config[1]['success_rate']):.1%}"
    ])
    
    # Correlação mais forte
    strongest_corr = max(analysis["parameter_correlations"].items(), 
                        key=lambda x: abs(x[1]))
    analysis["insights"].append(
        f"Parâmetro com maior impacto: {strongest_corr[0]} (correlação: {strongest_corr[1]:.3f})"
    )
    
    with open(output_filename, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    return analysis

def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python analyze_experiment_3.py <arquivo_exp_3.json>")
        print("📁 Procure arquivos em: datasets/exp_3_*.json")
        return 1
    
    filename = sys.argv[1]
    
    if not os.path.exists(filename):
        print(f"❌ Arquivo não encontrado: {filename}")
        return 1
    
    print(f"🔍 Analisando resultados do Experimento 3: {filename}")
    
    # Carregar dados
    data = load_experiment_3_data(filename)
    if not data:
        return 1
    
    # Análise
    df = analyze_parameter_impact(data)
    config_stats = generate_comparison_report(df)
    
    # Gerar outputs
    base_name = Path(filename).stem
    output_dir = f"reports/exp_3_analysis_{base_name}"
    analysis_file = f"{output_dir}/detailed_analysis.json"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Análise detalhada
    detailed_analysis = generate_detailed_analysis(data, analysis_file)
    print(f"\n📄 Análise detalhada salva em: {analysis_file}")
    
    # Visualizações (se matplotlib estiver disponível)
    try:
        create_visualizations(df, output_dir)
    except ImportError:
        print("⚠️  matplotlib não disponível - visualizações não foram criadas")
        print("   Instale com: pip install matplotlib pandas")
    
    print(f"\n✅ Análise do Experimento 3 concluída!")
    print(f"📁 Resultados em: {output_dir}/")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
