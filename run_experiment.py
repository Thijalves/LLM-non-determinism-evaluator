#!/usr/bin/env python3
"""
Script auxiliar para executar os experimentos com verificação de ambiente
"""

import sys
import subprocess
import platform
import os

def check_python():
    """Verifica se o Python está disponível"""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python encontrado: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("❌ Python não encontrado ou não configurado corretamente.")
    print("Por favor, instale o Python 3.8+ ou configure o PATH.")
    return False

def check_ollama():
    """Verifica se o Ollama está disponível"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            if "llama3.2" in result.stdout:
                print("✅ Ollama e llama3.2 encontrados")
                return True
            else:
                print("⚠️  Ollama encontrado, mas llama3.2 não está instalado")
                print("Execute: ollama pull llama3.2")
                return False
    except:
        pass
    
    print("❌ Ollama não encontrado")
    print("Instale o Ollama: https://ollama.com/download")
    return False

def install_requirements():
    """Instala as dependências do requirements.txt"""
    try:
        print("📦 Instalando dependências...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso")
            return True
        else:
            print(f"❌ Erro ao instalar dependências: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def run_experiment(experiment_num, tasks=10):
    """Executa um experimento específico"""
    if experiment_num not in [1, 2, 3]:
        print("❌ Número de experimento inválido. Use 1, 2 ou 3.")
        return False
    
    script_name = f"experiment_{experiment_num}.py"
    
    if not os.path.exists(script_name):
        print(f"❌ Script {script_name} não encontrado")
        return False
    
    print(f"\n🚀 Executando Experimento {experiment_num}...")
    print(f"📊 Tasks: {tasks}")
    
    # Modifica temporariamente o número de tasks se necessário
    if experiment_num == 3 and tasks != 10:
        with open(script_name, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified_content = content.replace('total_tasks = 10', f'total_tasks = {tasks}')
        
        with open(f"{script_name}.tmp", 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        try:
            result = subprocess.run([sys.executable, f"{script_name}.tmp"], 
                                  capture_output=False, text=True)
            return result.returncode == 0
        finally:
            os.remove(f"{script_name}.tmp")
    else:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, text=True)
        return result.returncode == 0

def main():
    print("🔬 LLM Non-Determinism Evaluator - Setup & Runner")
    print("=" * 50)
    
    # Verificações básicas
    if not check_python():
        return 1
    
    if not check_ollama():
        return 1
    
    # Instalar dependências
    if not install_requirements():
        return 1
    
    print("\n" + "=" * 50)
    print("📋 Experimentos Disponíveis:")
    print("1. Experimento 1: 5 soluções por task (baseline)")
    print("2. Experimento 2: Iteração com feedback")
    print("3. Experimento 3: Variação de parâmetros")
    print("=" * 50)
    
    try:
        exp_choice = input("\nEscolha o experimento (1-3): ").strip()
        if not exp_choice.isdigit() or int(exp_choice) not in [1, 2, 3]:
            print("❌ Escolha inválida")
            return 1
        
        exp_num = int(exp_choice)
        
        tasks_input = input(f"Número de tasks (padrão: 10, máximo: 164): ").strip()
        tasks = 10
        if tasks_input.isdigit():
            tasks = min(int(tasks_input), 164)
        
        print(f"\n🎯 Executando Experimento {exp_num} com {tasks} tasks...")
        
        success = run_experiment(exp_num, tasks)
        
        if success:
            print(f"\n✅ Experimento {exp_num} concluído com sucesso!")
            print("📁 Verifique os arquivos em:")
            print("   - datasets/ (resultados)")
            print("   - reports/ (análises)")
        else:
            print(f"\n❌ Experimento {exp_num} falhou")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Experimento interrompido pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
