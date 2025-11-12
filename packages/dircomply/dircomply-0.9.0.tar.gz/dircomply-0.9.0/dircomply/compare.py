"""
compare.py

Author: Benevant Mathew
Date: 2025-09-21
"""
import os

from dircomply.config.config import content_exts, existence_exts
from dircomply.utils import get_files_with_extensions
from dircomply.read import read_file

def compare_folders(folder1, folder2):
    """
    compare_folders
    Function to compare folders
    """
    # Separate by category
    folder1_content = get_files_with_extensions(folder1, content_exts)
    folder2_content = get_files_with_extensions(folder2, content_exts)

    folder1_exist = get_files_with_extensions(folder1, existence_exts)
    folder2_exist = get_files_with_extensions(folder2, existence_exts)

    # Combine sets
    folder1_files = folder1_content | folder1_exist
    folder2_files = folder2_content | folder2_exist

    # Common files
    common_files = folder1_files & folder2_files

    # Unique files
    unique_to_folder1 = folder1_files - folder2_files
    unique_to_folder2 = folder2_files - folder1_files

    different_files = []

    # Only compare contents for content_exts
    for file in common_files:
        if file.endswith(content_exts):
            path1 = os.path.join(folder1, file)
            path2 = os.path.join(folder2, file)
            if read_file(path1) != read_file(path2):
                different_files.append(file)

    return sorted(different_files), sorted(unique_to_folder1), sorted(unique_to_folder2)
