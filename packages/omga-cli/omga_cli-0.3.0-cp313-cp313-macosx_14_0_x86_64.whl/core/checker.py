import ast
import importlib.util
import os
from core.ai import ask
from core.utils import read_file
from core.logger import logger

def find_file(file_name: str, base_dir: str = os.getcwd()) -> str | None:
    """search in directory"""
    for root, _, files in os.walk(base_dir):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def check_syntax_py(path: str) -> tuple[bool, list[str]]:
    try:
        file_path = find_file(path) if not os.path.isabs(path) else path
        if not file_path or not os.path.exists(file_path):
            return False, [f"File not found: {path}"]
        
        if not file_path.endswith('.py'):
            return False, [f"Invalid file type: {path}. Only Python (.py) files are supported."]

        code = read_file(file_path)
        ast.parse(code)
        messages = []
        # Optional flake8
        if importlib.util.find_spec('flake8'):
            from flake8.api import legacy
            style_guide = legacy.get_style_guide(ignore=['E501'])
            report = style_guide.check_files([file_path])
            messages = [f"{line}" for line in report.get_statistics('E') + report.get_statistics('W')]
        return True, messages
    except SyntaxError as e:
        return False, [str(e)]
    except Exception as e:
        logger.error(f"Check error: {e}")
        return False, [str(e)]

def quick_fix_suggestion(path: str) -> str:
    file_path = find_file(path) if not os.path.isabs(path) else path
    if not file_path or not os.path.exists(file_path):
        return f"File not found: {path}"
    if not file_path.endswith('.py'):
        return f"Invalid file type: {path}. Only Python (.py) files are supported."
    ok, messages = check_syntax_py(file_path)
    if ok and not messages:
        return "No issues found."
    prompt = f"Summarize errors and suggest quick fixes: {', '.join(messages)}"
    return ask(prompt)