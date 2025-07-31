# LLM-non-determinism-evaluator
Este é o projeto da disciplina de tópicos avançados em engenharia de software. Nele iremos iterar sobre o trabalho [An Empirical Study of the Non-Determinism of ChatGPT in Code Generation](https://dl.acm.org/doi/full/10.1145/36970100). A equipe pretende aplicar as seguintes análises:
- Aplicar e avaliar o não determinismo em diferentes modelos de linguagem;
- Implementar loops para garantir corretude do código gerado.
- Analisar a intersecção entre corretude semântica e sintática do código gerado.

## Preparing the model

```sh
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

## Estrutura do Projeto

```
LLM-non-determinism-evaluator/
├── datasets/                    # Dataset e resultados dos experimentos
│   ├── human_eval.json         # Dataset HumanEval
│   └── exp_1_*.json           # Resultados dos experimentos
├── reports/                    # Relatórios e visualizações
│   ├── analysis/              # Relatórios de análise JSON
│   └── visualizations/        # Gráficos e matrizes PNG
├── utils/                     # Módulos auxiliares
│   ├── analysis.py           # Análise sintática e semântica
│   ├── dataset_handler.py    # Manipulação do dataset
│   ├── llm_handler.py        # Interface com o modelo LLM
│   └── module_loader.py      # Carregamento de módulos
├── current_task/              # Diretório temporário para tarefas
├── experiment_1.py           # Experimento principal
├── analyze_results.py        # Script de análise
├── visualize_results.py      # Script de visualização
├── cleanup.py               # Script de limpeza e organização
└── requirements.txt          # Dependências Python
```

## Experimentos 

1. **Experimento 1**: Coletar 5 soluções por task geradas pelo llama3.2 e comparar sintaxe (conteudo da string), semântica (resultado do teste) e estrutura (AST)
2. **Experimento 2**: Iteração com feedback até obter solução correta (máximo 5 tentativas)
3. **Experimento 3**: Variação de parâmetros do modelo - 5 configurações diferentes por task:
   - Conservative (temp=0.1, top_p=0.8, top_k=20)
   - Balanced (temp=0.7, top_p=0.9, top_k=40) 
   - Creative (temp=1.2, top_p=0.95, top_k=80)
   - High_Randomness (temp=1.5, top_p=1.0, top_k=100)
   - Focused (temp=0.3, top_p=0.7, top_k=10)

## Como Usar

### 1. Executar Experimento 1
```bash
python3 experiment_1.py
```
- Gera 5 soluções por tarefa
- Executa testes automáticos
- Salva resultados em `datasets/exp_1_*.json`
- Gera análise automática em `reports/analysis/analysis_report_*.json`

### 2. Executar Experimento 2
```bash
python3 experiment_2.py
```
- Itera até obter solução correta (máx 5 tentativas)
- Usa feedback dos erros para melhorar próxima tentativa
- Salva resultados em `datasets/exp_2_*.json`

### 3. Executar Experimento 3
```bash
python3 experiment_3.py
```
- Testa 5 configurações diferentes de parâmetros por task
- Avalia impacto da temperature, top_p, top_k e num_predict
- Salva resultados em `datasets/exp_3_*.json`
- Gera análise comparativa por configuração

### 2. Analisar Resultados
```bash
# Análise geral
python3 analyze_results.py datasets/exp_1_250728-202215.json

# Análise de tarefa específica
python3 analyze_results.py datasets/exp_1_250728-202215.json HumanEval_0
```

### 3. Criar Visualizações
```bash
python3 visualize_results.py datasets/exp_1_250728-202215.json
```
- Gera gráficos em `reports/visualizations/visualization_*.png`
- Gera matrizes de similaridade em `reports/visualizations/comparison_matrix_*.png`
```

## Métricas Implementadas

### Análise Sintática
- **Similaridade de strings** (difflib)
- **Similaridade de tokens** (identificadores, funções)
- **Hash MD5** para match exato
- **Normalização** de código

### Análise Estrutural (AST)
- **Estrutura de funções** (nome, argumentos, decoradores)
- **Controle de fluxo** (if, for, while)
- **Imports e expressões**
- **Similaridade estrutural**

### Análise Semântica
- **Taxa de sucesso** nos testes
- **Consistência semântica** (todas passam ou todas falham)
- **Score de não-determinismo** (1 - similaridade média)

## Exemplo de Resultados

Para HumanEval_0 (has_close_elements):
```
📊 Análise para HumanEval_0:
   • Taxa de sucesso: 80.00%
   • Similaridade sintática média: 52.97%
   • Similaridade AST média: 87.54%
   • Score de não-determinismo: 47.03%
   • Consistência semântica: ❌
```

## Organização de Arquivos

### Resultados dos Experimentos
- **Localização**: `datasets/exp_1_*.json`
- **Conteúdo**: Código gerado, resultados de teste, análises
- **Formato**: JSON com timestamp

### Relatórios de Análise
- **Localização**: `reports/analysis/analysis_report_*.json`
- **Conteúdo**: Métricas de similaridade, estatísticas agregadas
- **Formato**: JSON estruturado

### Visualizações
- **Localização**: `reports/visualizations/`
- **Tipos**: Gráficos de barras, matrizes de similaridade
- **Formato**: PNG de alta resolução

## Próximos Passos

1. **Expandir para 164 tarefas** (dataset completo)
2. **Testar outros modelos** (codellama, mistral)
3. **Adicionar mais métricas** (complexidade ciclomática)
4. **Implementar análise temporal**
5. **Criar dashboard interativo**

## Manutenção

O script `cleanup.py` ajuda a manter a organização:
- **Limpa arquivos temporários** do `current_task/`
- **Mantém apenas os últimos 5 relatórios** de análise
- **Mantém apenas as últimas 10 visualizações**
- **Cria backups** dos arquivos importantes