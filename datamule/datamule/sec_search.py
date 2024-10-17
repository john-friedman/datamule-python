import os
import re

def search(directory, keyword):
    results = []
    keyword = keyword.lower()  # Convert keyword to lowercase
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.xml', '.html', '.txt','.htm')):  # Add more extensions if needed
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()  # Convert content to lowercase
                        if keyword in content:  # Simple string search instead of regex
                            results.append(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")
    
    return results