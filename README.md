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

## Experimentos 

1. Coletar 5 soluções por task geradas pelo llama3.2 e comparar sintaxe (conteudo da string), semântica (resultado do teste) e estrutura (AST)