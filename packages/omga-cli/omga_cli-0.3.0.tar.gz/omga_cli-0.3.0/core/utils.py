import subprocess
import difflib
import os
from pathlib import Path

def read_file(path: str) -> str:
    """Read file with smart path resolution"""
    # Convert to Path object for better handling
    file_path = Path(path)
    
    # If it's already absolute, use as is
    if file_path.is_absolute():
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Try relative to current working directory
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Try relative to home directory
    home_path = Path.home() / path
    if home_path.exists():
        with open(home_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Try expanding user path (~)
    expanded_path = Path(path).expanduser()
    if expanded_path.exists():
        with open(expanded_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # If still not found, try to find it in common locations
    current_dir = Path.cwd()
    search_paths = [
        current_dir / path,
        current_dir / ".." / path,
        current_dir / "../.." / path,
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            with open(search_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    raise FileNotFoundError(f"File not found: {path}")

def write_file(path: str, content: str):
    with open(path, 'w') as f:
        f.write(content)

def run_subprocess(cmd: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)

def diff_text(old: str, new: str) -> str:
    diff = difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm='')
    return '\n'.join(diff)