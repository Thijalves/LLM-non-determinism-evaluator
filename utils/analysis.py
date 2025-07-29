import ast
import difflib
from typing import List, Dict, Tuple, Any
import hashlib
from collections import Counter

def analyze_syntax_similarity(code1: str, code2: str) -> Dict[str, Any]:
    """
    Analisa a similaridade sintática entre dois códigos.
    
    Args:
        code1: Primeiro código como string
        code2: Segundo código como string
        
    Returns:
        Dicionário com métricas de similaridade sintática
    """
    # Normalizar código (remover espaços extras, quebras de linha)
    def normalize_code(code: str) -> str:
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    norm_code1 = normalize_code(code1)
    norm_code2 = normalize_code(code2)
    
    # Calcular hash para comparação exata
    hash1 = hashlib.md5(norm_code1.encode()).hexdigest()
    hash2 = hashlib.md5(norm_code2.encode()).hexdigest()
    
    # Similaridade usando difflib
    similarity = difflib.SequenceMatcher(None, norm_code1, norm_code2).ratio()
    
    # Análise de tokens (palavras-chave, identificadores, etc.)
    def extract_tokens(code: str) -> List[str]:
        try:
            tree = ast.parse(code)
            tokens = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    tokens.append(f"NAME:{node.id}")
                elif isinstance(node, ast.FunctionDef):
                    tokens.append(f"FUNC:{node.name}")
                elif isinstance(node, ast.ClassDef):
                    tokens.append(f"CLASS:{node.name}")
                elif isinstance(node, ast.Constant):
                    tokens.append(f"CONST:{type(node.value).__name__}")
            return tokens
        except:
            return []
    
    tokens1 = extract_tokens(code1)
    tokens2 = extract_tokens(code2)
    
    # Similaridade de tokens
    token_similarity = 0
    if tokens1 or tokens2:
        token_similarity = difflib.SequenceMatcher(None, tokens1, tokens2).ratio()
    
    return {
        "exact_match": hash1 == hash2,
        "similarity_ratio": similarity,
        "token_similarity": token_similarity,
        "length_diff": abs(len(norm_code1) - len(norm_code2)),
        "hash1": hash1,
        "hash2": hash2
    }

def analyze_ast_structure(code1: str, code2: str) -> Dict[str, Any]:
    """
    Analisa a similaridade estrutural usando AST.
    
    Args:
        code1: Primeiro código como string
        code2: Segundo código como string
        
    Returns:
        Dicionário com métricas de similaridade estrutural
    """
    def extract_ast_structure(code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(code)
            structure = {
                "function_defs": [],
                "classes": [],
                "imports": [],
                "control_flow": [],
                "expressions": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    structure["function_defs"].append({
                        "name": node.name,
                        "args": len(node.args.args),
                        "decorators": len(node.decorator_list)
                    })
                elif isinstance(node, ast.ClassDef):
                    structure["classes"].append({
                        "name": node.name,
                        "bases": len(node.bases)
                    })
                elif isinstance(node, ast.Import):
                    structure["imports"].extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    structure["imports"].append(f"{node.module}.{', '.join([alias.name for alias in node.names])}")
                elif isinstance(node, (ast.If, ast.For, ast.While)):
                    structure["control_flow"].append(type(node).__name__)
                elif isinstance(node, ast.Expr):
                    structure["expressions"].append(type(node.value).__name__)
            
            return structure
        except:
            return {"function_defs": [], "classes": [], "imports": [], "control_flow": [], "expressions": []}
    
    struct1 = extract_ast_structure(code1)
    struct2 = extract_ast_structure(code2)
    
    # Calcular similaridade estrutural
    def calculate_structure_similarity(s1: Dict, s2: Dict) -> float:
        total_similarity = 0
        count = 0
        
        for key in s1.keys():
            if key in s2:
                if isinstance(s1[key], list) and isinstance(s2[key], list):
                    # Similaridade de listas
                    similarity = difflib.SequenceMatcher(None, str(s1[key]), str(s2[key])).ratio()
                else:
                    # Similaridade de valores
                    similarity = 1.0 if s1[key] == s2[key] else 0.0
                
                total_similarity += similarity
                count += 1
        
        return total_similarity / count if count > 0 else 0.0
    
    structure_similarity = calculate_structure_similarity(struct1, struct2)
    
    return {
        "structure_similarity": structure_similarity,
        "structure1": struct1,
        "structure2": struct2,
        "function_count_diff": abs(len(struct1["function_defs"]) - len(struct2["function_defs"])),
        "import_count_diff": abs(len(struct1["imports"]) - len(struct2["imports"]))
    }

def analyze_semantic_similarity(test_results: List[str]) -> Dict[str, Any]:
    """
    Analisa a similaridade semântica baseada nos resultados dos testes.
    
    Args:
        test_results: Lista de resultados de teste ("passed" ou "failed")
        
    Returns:
        Dicionário com métricas de similaridade semântica
    """
    passed_count = test_results.count("passed")
    failed_count = test_results.count("failed")
    total_count = len(test_results)
    
    # Taxa de sucesso
    success_rate = passed_count / total_count if total_count > 0 else 0
    
    # Consistência semântica (todas passaram ou todas falharam)
    all_passed = all(result == "passed" for result in test_results)
    all_failed = all(result == "failed" for result in test_results)
    consistent = all_passed or all_failed
    
    return {
        "success_rate": success_rate,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "total_count": total_count,
        "semantic_consistency": consistent,
        "all_passed": all_passed,
        "all_failed": all_failed
    }

def compare_solutions(solutions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compara múltiplas soluções para uma mesma tarefa.
    
    Args:
        solutions: Lista de soluções com campos "code" e "test_result"
        
    Returns:
        Dicionário com análise completa de similaridade
    """
    codes = [sol["code"] for sol in solutions]
    test_results = [sol["test_result"] for sol in solutions]
    
    # Análise sintática entre pares
    syntax_comparisons = []
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            syntax_analysis = analyze_syntax_similarity(codes[i], codes[j])
            ast_analysis = analyze_ast_structure(codes[i], codes[j])
            
            syntax_comparisons.append({
                "pair": (i, j),
                "syntax": syntax_analysis,
                "ast": ast_analysis
            })
    
    # Análise semântica
    semantic_analysis = analyze_semantic_similarity(test_results)
    
    # Estatísticas gerais
    exact_matches = sum(1 for comp in syntax_comparisons if comp["syntax"]["exact_match"])
    avg_similarity = sum(comp["syntax"]["similarity_ratio"] for comp in syntax_comparisons) / len(syntax_comparisons) if syntax_comparisons else 0
    avg_ast_similarity = sum(comp["ast"]["structure_similarity"] for comp in syntax_comparisons) / len(syntax_comparisons) if syntax_comparisons else 0
    
    return {
        "semantic_analysis": semantic_analysis,
        "syntax_comparisons": syntax_comparisons,
        "summary": {
            "total_solutions": len(solutions),
            "exact_matches": exact_matches,
            "avg_syntax_similarity": avg_similarity,
            "avg_ast_similarity": avg_ast_similarity,
            "non_determinism_score": 1 - avg_similarity  # Quanto menor a similaridade, maior o não-determinismo
        }
    }

def generate_analysis_report(task_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gera um relatório completo de análise para todas as tarefas.
    
    Args:
        task_results: Lista de resultados de tarefas
        
    Returns:
        Relatório completo de análise
    """
    all_analyses = []
    
    for task_result in task_results:
        if "responses" in task_result and len(task_result["responses"]) > 1:
            analysis = compare_solutions(task_result["responses"])
            analysis["task_id"] = task_result["task_id"]
            all_analyses.append(analysis)
    
    # Estatísticas agregadas
    if all_analyses:
        avg_non_determinism = sum(analysis["summary"]["non_determinism_score"] for analysis in all_analyses) / len(all_analyses)
        avg_success_rate = sum(analysis["semantic_analysis"]["success_rate"] for analysis in all_analyses) / len(all_analyses)
        consistent_tasks = sum(1 for analysis in all_analyses if analysis["semantic_analysis"]["semantic_consistency"])
        
        return {
            "task_analyses": all_analyses,
            "aggregate_stats": {
                "total_tasks": len(all_analyses),
                "avg_non_determinism_score": avg_non_determinism,
                "avg_success_rate": avg_success_rate,
                "semantically_consistent_tasks": consistent_tasks,
                "semantically_inconsistent_tasks": len(all_analyses) - consistent_tasks
            }
        }
    
    return {"task_analyses": [], "aggregate_stats": {}} 