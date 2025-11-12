"""
read.py

Author: Benevant Mathew
Date: 2025-09-21
"""
# Function to read file content
def read_file(filepath):
    """
    read_file
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        try:
            # Handles utf-8 with BOM
            with open(filepath, 'r', encoding='utf-8-sig') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"
    