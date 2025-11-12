# 📁 dircomply - Folder Comparison Tool

`dircomply` is a lightweight tool to compare files between two directories.It highlights files that differ and those that are unique to each folder.Supports both CLI mode and GUI mode for ease of use.

## ✅ Features

- Compare files between two folders
- Detect differences in file contents
- List unique files in each folder
- Supported filetypes are listed later
- GUI mode for interactive comparison
- CLI mode for quick terminal use

## 💾 Installation

Install dircomply using pip:

```sh
pip install dircomply
```

## 🧪 Example Usage

Compare two folders via CLI:

```sh
dircomply /path/to/folder1 /path/to/folder2
```

Launch GUI mode:

```sh
dircomply
```

Show version info:

```sh
dircomply --version
```

Display author details:

```sh
dircomply --author
```

## 📌 Supported CLI Options

Option Description
--help, -h Show help message and exit
--version, -v Show version number and exit
--author, -a Show author name and exit
--email, -e Show author email and exit
If no arguments are passed, GUI mode will be launched.

## 🔎 What Gets Compared?

dircomply compares only files with the following extensions:
```
        ".txt", ".py", ".bat", ".html", ".ts",".json",".scss",".tcl",".md",
        ".yaml",".yml",".ini",".in",".sh",".gitignore"
```

Also check below files on existence check rather than the content difference check.
```
        ".xlsx", ".csv", ".docx",
        ".png",".jpeg",".jpg",".ods",
        ".pdf"
```

All other file types are ignored during the comparison.
