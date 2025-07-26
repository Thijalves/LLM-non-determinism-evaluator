import json
import os

def extract_tests_from_json(json_file_path):
    """
    Reads a JSON file and extracts test content to individual files.
    
    Args:
        json_file_path (str): Path to the JSON file
    """
    # Create tests directory if it doesn't exist
    tests_dir = "tests"
    if not os.path.exists(tests_dir):
        os.makedirs(tests_dir)
        print(f"Created directory: {tests_dir}")
    
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if data is a list
        if not isinstance(data, list):
            print("Error: JSON file should contain a list of objects")
            return
        
        # Process each object in the list
        for i, obj in enumerate(data):
            # Validate required fields
            if 'task_id' not in obj:
                print(f"Warning: Object at index {i} missing 'task_id' field, skipping...")
                continue
            
            if 'test' not in obj:
                print(f"Warning: Object with task_id '{obj['task_id']}' missing 'test' field, skipping...")
                continue
            
            task_id = obj['task_id'].replace('/', '_')
            test_content = obj['test']

            
            # Create filename
            filename = f"{task_id}.py"
            filepath = os.path.join(tests_dir, filename)
            
            # Write test content to file
            try:
                with open(filepath, 'w', encoding='utf-8') as test_file:
                    test_file.write(test_content)
                print(f"Created test file: {filepath}")
            
            except Exception as e:
                print(f"Error writing file {filepath}: {e}")
    
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file_path}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Replace 'your_file.json' with the actual path to your JSON file
    json_file_path = "human_eval.json"
    extract_tests_from_json(json_file_path)