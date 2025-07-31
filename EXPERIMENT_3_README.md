# Experimento 3: Variação de Parâmetros do Modelo

## Objetivo

O Experimento 3 avalia como diferentes configurações de parâmetros do modelo Llama3.2 afetam o não-determinismo e a qualidade das soluções geradas. Testamos 5 configurações distintas para cada task do HumanEval.

## Configurações Testadas

### 1. Conservative (Conservadora)
- **Temperature:** 0.1 (baixa criatividade)
- **Top-p:** 0.8 (amostragem nuclear restrita)
- **Top-k:** 20 (poucas opções consideradas)
- **Num_predict:** 256 (respostas mais curtas)
- **Objetivo:** Respostas mais determinísticas e focadas

### 2. Balanced (Balanceada)
- **Temperature:** 0.7 (criatividade moderada)
- **Top-p:** 0.9 (amostragem nuclear padrão)
- **Top-k:** 40 (opções moderadas)
- **Num_predict:** 512 (tamanho padrão)
- **Objetivo:** Configuração equilibrada (baseline)

### 3. Creative (Criativa)
- **Temperature:** 1.2 (alta criatividade)
- **Top-p:** 0.95 (amostragem nuclear ampla)
- **Top-k:** 80 (muitas opções)
- **Num_predict:** 512 (tamanho padrão)
- **Objetivo:** Soluções mais criativas e variadas

### 4. High_Randomness (Alta Aleatoriedade)
- **Temperature:** 1.5 (muito alta criatividade)
- **Top-p:** 1.0 (sem restrição de amostragem)
- **Top-k:** 100 (máximas opções)
- **Num_predict:** 768 (respostas mais longas)
- **Objetivo:** Máxima variabilidade e exploração

### 5. Focused (Focada)
- **Temperature:** 0.3 (baixa criatividade)
- **Top-p:** 0.7 (amostragem restrita)
- **Top-k:** 10 (muito poucas opções)
- **Num_predict:** 300 (respostas curtas-médias)
- **Objetivo:** Respostas altamente determinísticas

## Como Executar

### Método 1: Script Auxiliar (Recomendado)
```bash
python run_experiment.py
# Escolha a opção 3 para Experimento 3
```

### Método 2: Execução Direta
```bash
# Para 10 tasks (teste rápido)
python experiment_3.py

# Para todas as 164 tasks (experimento completo)
# Edite experiment_3.py e altere total_tasks = 164
```

## Resultados

### Arquivos Gerados
- `datasets/exp_3_llama3_params_TIMESTAMP.json` - Dados brutos
- `reports/analysis_exp_3_params_TIMESTAMP.json` - Análise automática
- `reports/exp_3_analysis_*/` - Análise detalhada (via script de análise)

### Estrutura dos Dados
```json
{
  "task_id": "HumanEval_0",
  "responses": [
    {
      "config_name": "Conservative",
      "model_params": {
        "temperature": 0.1,
        "top_p": 0.8,
        "top_k": 20,
        "num_predict": 256
      },
      "code": "...",
      "traceback": "",
      "test_result": "passed"
    }
  ]
}
```

## Análise dos Resultados

### Análise Automática
```bash
python analyze_experiment_3.py datasets/exp_3_llama3_params_TIMESTAMP.json
```

### Métricas Avaliadas
1. **Taxa de Sucesso por Configuração**
2. **Correlação entre Parâmetros e Performance**
3. **Comprimento Médio do Código**
4. **Variabilidade entre Soluções**
5. **Análise de Timeout e Erros**

### Visualizações Geradas
- Taxa de sucesso por configuração (gráfico de barras)
- Relação Temperature vs Sucesso (scatter plot)
- Distribuição do comprimento do código (box plot)
- Matriz de correlação entre parâmetros

## Hipóteses Testadas

### H1: Temperature Baixa → Maior Determinismo
**Expectativa:** Configurações Conservative e Focused devem ter menor variabilidade

### H2: Temperature Alta → Maior Criatividade
**Expectativa:** Configurações Creative e High_Randomness podem gerar soluções mais diversas

### H3: Top-k/Top-p → Qualidade vs Diversidade
**Expectativa:** Valores menores podem aumentar a qualidade, mas reduzir a diversidade

### H4: Num_predict → Completude das Soluções
**Expectativa:** Valores maiores podem levar a soluções mais completas

## Interpretação dos Resultados

### Correlações Esperadas
- **Temperature ↔ Variabilidade:** Correlação positiva
- **Top-k ↔ Diversidade:** Correlação positiva  
- **Top-p ↔ Criatividade:** Correlação positiva
- **Num_predict ↔ Completude:** Correlação positiva

### Métricas de Interesse
1. **Determinismo:** Configurações que geram soluções mais similares
2. **Performance:** Taxa de sucesso nos testes
3. **Eficiência:** Tempo e recursos utilizados
4. **Diversidade:** Variação entre soluções

## Limitações

1. **Timeout:** Algumas configurações podem gerar código que não termina
2. **Contexto:** Parâmetros podem ter efeitos diferentes dependendo da task
3. **Hardware:** Performance pode variar entre diferentes máquinas
4. **Modelo:** Resultados específicos para Llama3.2

## Próximos Passos

1. **Análise Estatística:** Testes de significância entre configurações
2. **Análise Qualitativa:** Avaliação manual da qualidade das soluções
3. **Otimização:** Busca por configurações otimais para diferentes tipos de task
4. **Comparação:** Avaliar diferentes modelos com as mesmas configurações

---

**Nota:** Este experimento faz parte do projeto de Tópicos Avançados em Engenharia de Software, baseado no paper "An Empirical Study of the Non-Determinism of ChatGPT in Code Generation".
