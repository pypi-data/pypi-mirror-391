"""
gui.py

Author: Benevant Mathew
Date: 2025-09-21
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from dircomply.compare import compare_folders

def create_gui(folder1_path=None,folder2_path=None,compare_on_start=False):
    """
    create_gui
    # GUI Application
    """

    def select_folder1():
        path = filedialog.askdirectory(title="Select Folder 1")
        if path:
            folder1_var.set(path)

    def select_folder2():
        path = filedialog.askdirectory(title="Select Folder 2")
        if path:
            folder2_var.set(path)

    def compare():
        folder1 = folder1_var.get()
        folder2 = folder2_var.get()

        if not folder1 or not folder2:
            messagebox.showerror("Error", "Please select both folders")
            return

        if not os.path.exists(folder1) or not os.path.exists(folder2):
            messagebox.showerror("Error", "One or both folders do not exist")
            return

        # Compare folders
        different_files, unique_to_folder1, unique_to_folder2 = compare_folders(folder1, folder2)

        # Create result message
        result = f"Comparison Results: of {folder1} and {folder2}\n\n"
        if different_files:
            result += "Files with differences:\n" + "\n".join(different_files) + "\n\n"
        else:
            result += "No files with differences found.\n\n"

        if unique_to_folder1:
            result += f"Files unique to {folder1}:\n" + "\n".join(unique_to_folder1) + "\n\n"
        if unique_to_folder2:
            result += f"Files unique to {folder2}:\n" + "\n".join(unique_to_folder2) + "\n\n"

        # Display results in a popup window
        popup = tk.Toplevel(root)
        popup.title("Comparison Results")
        popup.geometry("600x400")

        result_text = tk.Text(popup, wrap=tk.WORD, font=("Arial", 10))
        result_text.pack(expand=True, fill=tk.BOTH)
        result_text.insert(tk.END, result)
        result_text.config(state=tk.DISABLED)
        scrollbar = tk.Scrollbar(popup, command=result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_text.config(yscrollcommand=scrollbar.set)


    # Main window
    root = tk.Tk()
    root.title("Folder File Comparator")
    root.geometry("500x300")

    folder1_var = tk.StringVar()
    folder2_var = tk.StringVar()
    if folder1_path:
        folder1_var.set(folder1_path)
    if folder2_path:
        folder2_var.set(folder2_path)

    # GUI Layout
    tk.Label(root, text="Folder 1 Path:", font=("Arial", 12)).pack(pady=5)
    tk.Entry(root, textvariable=folder1_var, width=50).pack()
    tk.Button(root, text="Select Folder 1", command=select_folder1).pack(pady=5)

    tk.Label(root, text="Folder 2 Path:", font=("Arial", 12)).pack(pady=5)
    tk.Entry(root, textvariable=folder2_var, width=50).pack()
    tk.Button(root, text="Select Folder 2", command=select_folder2).pack(pady=5)

    tk.Button(root, text="Compare Folders", command=compare, font=("Arial", 12, "bold"), bg="lightblue").pack(pady=20)
    if compare_on_start and folder1_path and folder2_path:
        compare()

    root.mainloop()
