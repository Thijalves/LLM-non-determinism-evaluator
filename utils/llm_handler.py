import os
import re
from ollama import chat
from ollama import ChatResponse

def generate_code(task: str, model: str, feedback=None, model_params=None):
    """Generate and save solution to a file"""

    code = ""
    while(code == ""):
        response = get_model_response(task, model, feedback=feedback, model_params=model_params)
        code = extract_code(response)
    return code
    
def save_solution(code: str, entry_point: str, destination: str):
    # rename method in code
    code = code.replace(entry_point, "generated_solution")
    
    filename = './generated_solution.py'
    save_to_file(code, os.path.join(destination, filename))

def extract_code(response: str) -> str:
    """Extract the Python code block from a Markdown-formatted string."""
    match = re.search(r"```python(.*?)```", response, re.DOTALL)
    return match.group(1).strip() if match else ""

def get_model_response(task:str, model: str, feedback=None, model_params=None) -> str:

    message = 'Generate Python3 code, no examples (Markdown):\n' + task

    if (feedback):
        message += "\nPrevious attempt failed with the following feedback:\n" + feedback        

    # Default model parameters
    options = {
        'temperature': 0.7,
        'top_p': 0.9,
        'top_k': 40,
        'num_predict': 512
    }
    
    # Override with custom parameters if provided
    if model_params:
        options.update(model_params)

    response: ChatResponse = chat(
        model=model, 
        messages=[
            {
                'role': 'user',
                'content': message,
            },
        ],
        options=options
    )

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