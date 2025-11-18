#!/usr/bin/env python3
"""
Copyright (C) 2025, Jabez Winston C

Author  : Jabez Winston C <jabezwinston@gmail.com>
License : MIT
Date    : 14-Nov-2025

Dump Project files to Markdown file
"""

import os
import sys
import argparse
from pathlib import Path


# Default extensions to exclude
DEFAULT_EXCLUDES = ['pyc', 'o', 'bin', 'hex', 'md', 'elf']

# Default folders to exclude
DEFAULT_FOLDER_EXCLUDES = ['__pycache__', 'node_modules', '.git', '.svn', '.hg', 'venv', 'env', '.venv', 'dist', 'build', '.idea', '.vscode']


def should_include_folder(foldername, folder_path, base_path, include_folders, exclude_folders):
    """Determine if a folder should be included based on include/exclude rules."""
    # Get relative path from base
    rel_path = os.path.relpath(folder_path, base_path)
    
    # Check exclude list first
    if foldername in exclude_folders or rel_path in exclude_folders:
        return False
    
    # Check if any parent path is in exclude list
    path_parts = Path(rel_path).parts
    for i in range(len(path_parts)):
        partial_path = os.path.join(*path_parts[:i+1])
        if partial_path in exclude_folders:
            return False
    
    # If include list is specified, folder must match
    if include_folders:
        return foldername in include_folders or rel_path in include_folders or any(
            rel_path.startswith(inc_folder) for inc_folder in include_folders
        )
    
    # If no include list, include all folders (except those excluded)
    return True


def generate_tree(directory, include_exts, exclude_exts, include_folders, exclude_folders, base_path, prefix="", is_last=True):
    """Generate a tree structure of the directory."""
    tree_lines = []
    
    try:
        entries = sorted(os.listdir(directory))
    except PermissionError:
        return tree_lines
    
    # Filter entries
    dirs = [e for e in entries if os.path.isdir(os.path.join(directory, e)) and not e.startswith('.')]
    
    # Filter directories by include/exclude rules
    dirs = [d for d in dirs if should_include_folder(d, os.path.join(directory, d), base_path, include_folders, exclude_folders)]
    
    files = [e for e in entries if os.path.isfile(os.path.join(directory, e))]
    
    # Filter files by extension
    files = [f for f in files if should_include_file(f, include_exts, exclude_exts)]
    
    all_entries = dirs + files
    
    for i, entry in enumerate(all_entries):
        is_last_entry = (i == len(all_entries) - 1)
        entry_path = os.path.join(directory, entry)
        
        # Tree characters
        connector = "└── " if is_last_entry else "├── "
        tree_lines.append(f"{prefix}{connector}{entry}")
        
        # Recurse into directories
        if os.path.isdir(entry_path) and not entry.startswith('.'):
            extension = "    " if is_last_entry else "│   "
            tree_lines.extend(generate_tree(entry_path, include_exts, exclude_exts, include_folders, exclude_folders, base_path, prefix + extension, is_last_entry))
    
    return tree_lines


def should_include_file(filename, include_exts, exclude_exts):
    """Determine if a file should be included based on include/exclude rules."""
    # Get file extension (without dot)
    ext = os.path.splitext(filename)[1][1:].lower() if '.' in filename else ''
    
    # Check exclude list first
    if ext in exclude_exts:
        return False
    
    # If include list is specified, file must match one of the extensions
    if include_exts:
        return ext in include_exts
    
    # If no include list, include all files (except those excluded)
    return True


def get_language_from_extension(ext):
    """Map file extension to markdown language identifier."""
    language_map = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'jsx': 'jsx',
        'tsx': 'tsx',
        'java': 'java',
        'c': 'c',
        'cpp': 'cpp',
        'cc': 'cpp',
        'cxx': 'cpp',
        'h': 'c',
        'hpp': 'cpp',
        'cs': 'csharp',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'php': 'php',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'html': 'html',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        'json': 'json',
        'xml': 'xml',
        'yaml': 'yaml',
        'yml': 'yaml',
        'md': 'markdown',
        'sh': 'bash',
        'bash': 'bash',
        'sql': 'sql',
        'r': 'r',
        'matlab': 'matlab',
        'm': 'matlab',
    }
    return language_map.get(ext.lower(), ext.lower())


def collect_files(directory, include_exts, exclude_exts, include_folders, exclude_folders):
    """Collect all files based on include/exclude rules."""
    files = []
    base_path = directory
    
    for root, dirs, filenames in os.walk(directory):
        # Skip hidden directories and apply folder filters
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   should_include_folder(d, os.path.join(root, d), base_path, include_folders, exclude_folders)]
        
        for filename in filenames:
            if should_include_file(filename, include_exts, exclude_exts):
                files.append(os.path.join(root, filename))
    
    return sorted(files)


def dump_to_markdown(folder_path, include_exts, exclude_exts, include_folders, exclude_folders, output_file):
    """Generate markdown file with all project files."""
    folder_path = Path(folder_path).resolve()
    folder_name = folder_path.name
    
    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        sys.exit(1)
    
    if not folder_path.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        sys.exit(1)
    
    # Generate markdown content
    markdown_lines = []
    markdown_lines.append(f"# {folder_name}\n")
    
    # Add folder structure tree
    markdown_lines.append("## Folder structure tree\n")
    markdown_lines.append("```")
    markdown_lines.append(folder_name + "/")
    tree_lines = generate_tree(folder_path, include_exts, exclude_exts, include_folders, exclude_folders, folder_path)
    markdown_lines.extend(tree_lines)
    markdown_lines.append("```\n")
    
    # Collect and dump files
    files = collect_files(folder_path, include_exts, exclude_exts, include_folders, exclude_folders)
    
    if not files:
        print("No files found matching the specified criteria.")
        return
    
    for file_path in files:
        # Get relative path from the base folder
        rel_path = os.path.relpath(file_path, folder_path)
        
        markdown_lines.append(f"## `{rel_path}`\n")
        
        # Get file extension for syntax highlighting
        ext = os.path.splitext(file_path)[1][1:]  # Remove the dot
        lang = get_language_from_extension(ext)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            markdown_lines.append(f"```{lang}")
            markdown_lines.append(content)
            markdown_lines.append("```\n")
        except UnicodeDecodeError:
            markdown_lines.append("```")
            markdown_lines.append("[Binary file - cannot display content]")
            markdown_lines.append("```\n")
        except Exception as e:
            markdown_lines.append("```")
            markdown_lines.append(f"[Error reading file: {str(e)}]")
            markdown_lines.append("```\n")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_lines))
    
    print(f"✓ Successfully dumped {len(files)} files to '{output_file}'")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Dump project files into a single markdown file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  projdump2md -i py,js,html -o project_dump.md
  projdump2md -i c,cpp,h -f /path/to/project
  projdump2md -e log,tmp -f . -o output.md
  projdump2md -i py -e pyc,pyo --no-default-excludes
  projdump2md -I src,lib -E tests,docs
  projdump2md -i py -I src -E __pycache__,venv
        """
    )
    
    parser.add_argument(
        '-i', '--include',
        type=str,
        help='Comma-separated list of file extensions to include (e.g., "py,js,html")',
        default=''
    )
    
    parser.add_argument(
        '-e', '--exclude',
        type=str,
        help='Comma-separated list of file extensions to exclude (e.g., "log,tmp")',
        default=''
    )
    
    parser.add_argument(
        '-I', '--include-folders',
        type=str,
        help='Comma-separated list of folder names/paths to include (e.g., "src,lib")',
        default=''
    )
    
    parser.add_argument(
        '-E', '--exclude-folders',
        type=str,
        help='Comma-separated list of folder names/paths to exclude (e.g., "tests,docs")',
        default=''
    )
    
    parser.add_argument(
        '--no-default-excludes',
        action='store_true',
        help='Disable default file exclusions (pyc, o, bin, hex, md, elf)'
    )
    
    parser.add_argument(
        '--no-default-folder-excludes',
        action='store_true',
        help='Disable default folder exclusions (__pycache__, node_modules, .git, etc.)'
    )
    
    parser.add_argument(
        '-f', '--folder',
        type=str,
        default='.',
        help='Folder path to scan (default: current directory ".")'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='project_dump.md',
        help='Output markdown file name (default: "project_dump.md")'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Parse include extensions
    include_exts = set(ext.strip().lower() for ext in args.include.split(',') if ext.strip()) if args.include else set()
    
    # Parse exclude extensions
    exclude_exts = set(ext.strip().lower() for ext in args.exclude.split(',') if ext.strip()) if args.exclude else set()
    
    # Add default excludes unless disabled
    if not args.no_default_excludes:
        exclude_exts.update(DEFAULT_EXCLUDES)
    
    # Parse include folders
    include_folders = set(folder.strip() for folder in args.include_folders.split(',') if folder.strip()) if args.include_folders else set()
    
    # Parse exclude folders
    exclude_folders = set(folder.strip() for folder in args.exclude_folders.split(',') if folder.strip()) if args.exclude_folders else set()
    
    # Add default folder excludes unless disabled
    if not args.no_default_folder_excludes:
        exclude_folders.update(DEFAULT_FOLDER_EXCLUDES)
    
    print(f"Scanning folder: {args.folder}")
    if include_exts:
        print(f"Include extensions: {', '.join(sorted(include_exts))}")
    else:
        print("Include extensions: All files")
    if exclude_exts:
        print(f"Exclude extensions: {', '.join(sorted(exclude_exts))}")
    if include_folders:
        print(f"Include folders: {', '.join(sorted(include_folders))}")
    if exclude_folders:
        print(f"Exclude folders: {', '.join(sorted(exclude_folders))}")
    print(f"Output file: {args.output}\n")
    
    dump_to_markdown(args.folder, include_exts, exclude_exts, include_folders, exclude_folders, args.output)


if __name__ == '__main__':
    main()