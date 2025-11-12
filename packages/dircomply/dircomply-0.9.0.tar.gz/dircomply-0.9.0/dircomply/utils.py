"""
utils.py

Author: Benevant Mathew
Date: 2025-09-21
"""
import os
import json
import importlib.resources


def get_files_with_extensions(folder, extensions):
    """
    get_files_with_extensions
    # Function to get all files with specific extensions
    """
    all_files = set()
    for root_dir, _, files in os.walk(folder):
        for file in files:
            if file.endswith(extensions):
                relative_path = os.path.relpath(os.path.join(root_dir, file), folder)
                all_files.add(relative_path)
    return all_files

def load_extensions():
    """
    Load extensions to compare.
    - "content_extensions" are compared by file contents
    - "existence_extensions" are only checked for presence
    """
    try:
        with importlib.resources.open_text("dircomply.config", "extensions.json") as f:
            data = json.load(f)
    except (FileNotFoundError, ImportError):
        local_path = os.path.join(os.path.dirname(__file__), "config", "extensions.json")
        with open(local_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

    return (
        tuple(data.get("content_extensions", [".txt", ".py", ".bat", ".html", ".ts"])),
        tuple(data.get("existence_extensions", [".xlsx", ".csv", ".docx"]))
    )



