import os
import re
from ollama import chat
from ollama import ChatResponse

def generate_solution(task: str, model: str, destination: str):
    """Generate and save solution to a file"""
    response = get_model_response(task, model)
    code = extract_code(response)

    filename = './generated_solution.py'
    save_to_file(code, os.path.join(destination, filename))

def extract_code(response: str) -> str:
    """Extract the Python code block from a Markdown-formatted string."""
    match = re.search(r"```python(.*?)```", response, re.DOTALL)
    return match.group(1).strip() if match else ""

def get_model_response(task:str, model: str) -> str:
    response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'user',
            'content': 'Generate Python3 code (Markdown):\n' + task,
        },
    ])
    return response['message']['content']

def save_to_file(content: str, filename: str):
    """
    Saves the content to a file.
    
    Args:
        content (str): The content to save
        filename (str): The name of the file to save the content to
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        # print(f"Created test file: {filename}")
    except Exception as e:
        print(f"Error writing file {filename}: {e}")