#!/usr/bin/env python3
"""
Script para limpar arquivos antigos e manter a organização do projeto.
"""

import os
import glob
from datetime import datetime, timedelta

def cleanup_old_files():
    """Remove arquivos antigos para manter a organização."""
    
    print("🧹 Iniciando limpeza de arquivos antigos...")
    
    # Limpar arquivos antigos do current_task
    current_task_files = glob.glob("current_task/*")
    if current_task_files:
        for file in current_task_files:
            try:
                os.remove(file)
                print(f"   ✅ Removido: {file}")
            except Exception as e:
                print(f"   ❌ Erro ao remover {file}: {e}")
    
    # Listar arquivos de relatório mais antigos (manter apenas os últimos 5)
    analysis_reports = sorted(glob.glob("reports/analysis/analysis_report_*.json"))
    if len(analysis_reports) > 5:
        old_reports = analysis_reports[:-5]
        for report in old_reports:
            try:
                os.remove(report)
                print(f"   ✅ Removido relatório antigo: {report}")
            except Exception as e:
                print(f"   ❌ Erro ao remover {report}: {e}")
    
    # Listar visualizações mais antigas (manter apenas as últimas 10)
    visualizations = sorted(glob.glob("reports/visualizations/*.png"))
    if len(visualizations) > 10:
        old_viz = visualizations[:-10]
        for viz in old_viz:
            try:
                os.remove(viz)
                print(f"   ✅ Removida visualização antiga: {viz}")
            except Exception as e:
                print(f"   ❌ Erro ao remover {viz}: {e}")
    
    print("✅ Limpeza concluída!")

def show_project_stats():
    """Mostra estatísticas do projeto."""
    
    print("\n📊 ESTATÍSTICAS DO PROJETO:")
    
    # Contar arquivos de resultados
    result_files = glob.glob("datasets/exp_1_*.json")
    print(f"   • Resultados de experimentos: {len(result_files)}")
    
    # Contar relatórios de análise
    analysis_files = glob.glob("reports/analysis/analysis_report_*.json")
    print(f"   • Relatórios de análise: {len(analysis_files)}")
    
    # Contar visualizações
    viz_files = glob.glob("reports/visualizations/*.png")
    print(f"   • Visualizações: {len(viz_files)}")
    
    # Mostrar arquivos mais recentes
    if result_files:
        latest_result = max(result_files, key=os.path.getctime)
        print(f"   • Resultado mais recente: {latest_result}")
    
    if analysis_files:
        latest_analysis = max(analysis_files, key=os.path.getctime)
        print(f"   • Análise mais recente: {latest_analysis}")

def create_backup():
    """Cria backup dos arquivos importantes."""
    
    timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    print(f"💾 Criando backup em: {backup_dir}")
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copiar resultados mais recentes
        result_files = glob.glob("datasets/exp_1_*.json")
        if result_files:
            latest_result = max(result_files, key=os.path.getctime)
            os.system(f"cp {latest_result} {backup_dir}/")
            print(f"   ✅ Backup do resultado: {latest_result}")
        
        # Copiar análise mais recente
        analysis_files = glob.glob("reports/analysis/analysis_report_*.json")
        if analysis_files:
            latest_analysis = max(analysis_files, key=os.path.getctime)
            os.system(f"cp {latest_analysis} {backup_dir}/")
            print(f"   ✅ Backup da análise: {latest_analysis}")
        
        # Copiar visualizações mais recentes
        viz_files = glob.glob("reports/visualizations/*.png")
        if viz_files:
            os.system(f"cp reports/visualizations/*.png {backup_dir}/")
            print(f"   ✅ Backup das visualizações")
        
        print(f"✅ Backup criado em: {backup_dir}")
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")

def main():
    """Função principal."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "cleanup":
            cleanup_old_files()
        elif command == "stats":
            show_project_stats()
        elif command == "backup":
            create_backup()
        else:
            print("❌ Comando inválido!")
            print("Uso: python cleanup.py [cleanup|stats|backup]")
    else:
        # Executar todas as operações
        cleanup_old_files()
        show_project_stats()
        print("\n💡 Dica: Use 'python cleanup.py backup' para criar backup")

if __name__ == "__main__":
    main() 