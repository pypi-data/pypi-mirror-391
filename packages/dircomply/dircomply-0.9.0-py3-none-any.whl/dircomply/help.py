"""
help.py

Author: Benevant Mathew
Date: 2025-09-21
"""
import sys
# Function to display help
def print_help():
    """
    help function
    """
    help_message = """
Usage: dircomply [OPTIONS]

A small package to compare the files between two project folders.

Options:
    --version, -v      Show the version of dircomply and exit
    --help, -h         Show this help message and exit
    --email, -e        Show email and exit
    --author, -a       Show author and exit
    (No arguments)     Launch the GUI application
    [folder1_path] [folder2_path] compare contents form both folders.
    """
    print(help_message)
    sys.exit(0)
    