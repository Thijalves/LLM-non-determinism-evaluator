import os
import re
import json
import importlib.util

def get_field_from_json(json_file_path: str, task_id: str, field: str) -> str:
    """
    Reads a JSON file and extracts the content for a specific task_id to an individual file.

    Args:
        json_file_path (str): Path to the JSON file
        task_id (str): The task_id to extract
        field(str): The field in the JSON object to extract and save
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise Exception("Error: JSON file should contain a list of objects")

        found = False
        for obj in data:
            if obj.get('task_id') == task_id:
                if field not in obj:
                    raise Exception(f"Warning: Object with task_id '{task_id}' missing {field} field, skipping...")

                content = obj.get(field)

                return content

        if not found:
            raise Exception(f"task_id '{task_id}' not found in JSON file")

    except FileNotFoundError:
        print(f"Error: JSON file '{json_file_path}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return ""

def get_canonical_solution(json_file_path: str, task_id: str) -> str:
    """
    Reads a JSON file and extracts the content for a specific task_id to an individual file.

    Args:
        json_file_path (str): Path to the JSON file
        task_id (str): The task_id to extract
        field (str): The field in the JSON object to extract and save
    """
    return (
        get_field_from_json(
            json_file_path,
            task_id,
            'prompt'
        ) + get_field_from_json(
            json_file_path,
            task_id,
            'canonical_solution'
            )
    )

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

def get_entrypoint(json_file_path: str, task_id: str) -> str:
    """Retrieves the entrypoint function name from a JSON file for a specific task_id.

    Args:
        json_file_path (str): Path to the JSON file
        task_id (str): The task_id to extract

    Returns:
        str: The entrypoint function name if found, otherwise an empty string
    """
    try:
        return get_field_from_json(json_file_path, task_id, 'entry_point')
    except Exception as e:
        print(f"Error retrieving entrypoint for task_id '{task_id}': {e}")   

    return ""

def get_task(json_file_path: str, task_id: str) -> str:
    """
    Retrieves the task prompt from a JSON file for a specific task_id.

    Args:
        json_file_path (str): Path to the JSON file
        task_id (str): The task_id to extract

    Returns:
        str: The task prompt if found, otherwise an empty string
    """
    try:
        return get_field_from_json(json_file_path, task_id, 'prompt')
    except Exception as e:
        print(f"Error retrieving task with task_id '{task_id}': {e}")

    return "" 

def rename_function_regex(code_str: str, new_name: str) -> str:
    # Match: def <func_name>(...):
    return re.sub(r'(?<=def )\w+', new_name, code_str, count=1)

def process_task(json_file_path: str, task_id: str, destination_path: str):
    # save canonical solution into a file
    content = get_canonical_solution(json_file_path, task_id)

    # process content so that the method name in it is caled solution
    content = rename_function_regex(content, 'canonical_solution')

    if content:
        filename = "canonical_solution.py"
        save_to_file(content, os.path.join(destination_path, filename))
    else:
        print(f"No content found for task_id '{task_id}'")

    # save test case into a file
    content = get_field_from_json(json_file_path, task_id, 'test')
    if content:
        filename = "test_case.py"
        save_to_file(content, os.path.join(destination_path, filename))
    else:
        print(f"No test case found for task_id '{task_id}'")

if __name__ == "__main__":
    ret = get_field_from_json("human_eval.json", "HumanEval_0", "canonical_solution")
    print(ret)