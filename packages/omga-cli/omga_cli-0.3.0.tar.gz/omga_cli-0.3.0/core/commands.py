from core.checker import check_syntax_py, quick_fix_suggestion
from core.ai import ask, ask_stream, explain_code, fix_code, suggest_improvements, generate_documentation
from core.utils import read_file, write_file, run_subprocess, diff_text
from core.config import CONFIG_DIR, get_config_value
from core.logger import logger
from core.ui import ui, MessageType
import os
import time
from typing import Tuple, Optional

def dispatch_command(text: str):
    """Enhanced command dispatcher with better error handling"""
    parts = text.split()
    if not parts:
        return
    
    cmd = parts[0].lower()
    args = ' '.join(parts[1:])
    
    handlers = {
        'help': lambda: help_handler(),
        'check': lambda: check_handler(args),
        'explain': lambda: explain_handler(args),
        'ask': lambda: ask_handler(args),
        'fix': lambda: fix_handler(args),
        'improve': lambda: improve_handler(args),
        'docs': lambda: docs_handler(args),
        'run': lambda: run_handler(args),
        'generate': lambda: generate_handler(parts[2], parts[3]) if len(parts) > 3 and parts[1] == 'project' else ui.print_error("Invalid generate command. Use: generate project <template> <name>"),
        'snippet': lambda: snippet_handler(parts[1], parts[2] if len(parts) > 2 else None, ' '.join(parts[3:]) if len(parts) > 3 else None),
        'config': lambda: config_handler(),
        'status': lambda: status_handler(),
    }
    
    if cmd in handlers:
        try:
            result = handlers[cmd]()
            if result:
                ui.print_message(str(result), MessageType.INFO)
        except Exception as e:
            ui.print_error(f"Error executing command '{cmd}': {e}")
    else:
        ui.print_error(f"Unknown command: {cmd}")
        ui.print_info("Type 'help' to see available commands")

def help_handler():
    """Show clean help"""
    commands = {
        "help": "Show this help message",
        "check <file>": "Check syntax and linting",
        "explain <file>": "Get AI code explanation",
        "ask <question>": "Ask AI questions",
        "fix <file>": "Fix code issues",
        "improve <file>": "Get improvement suggestions",
        "docs <file>": "Generate documentation",
        "run <command>": "Run shell commands",
        "generate project <template> <name>": "Create new project",
        "snippet add|list|remove": "Manage code snippets",
        "config": "Show configuration",
        "status": "Show system status",
        "exit": "Exit the shell"
    }
    
    ui.print_help(commands)
    return None

def check_handler(file: str):
    """Enhanced check handler with beautiful output"""
    try:
        ok, messages = check_syntax_py(file)
        
        if ok and not messages:
            ui.print_success(f"✅ {file} - No issues found!", "Code Analysis")
            return None
        elif ok:
            ui.print_warning(f"⚠️ {file} - Syntax OK, but has warnings", "Code Analysis")
            for msg in messages:
                ui.print_message(f"  • {msg}", MessageType.WARNING)
            return None
        else:
            ui.print_error(f"❌ {file} - Syntax errors found", "Code Analysis")
            for msg in messages:
                ui.print_message(f"  • {msg}", MessageType.ERROR)
            return None
            
    except Exception as e:
        ui.print_error(f"Error checking {file}: {e}")
        return None

def explain_handler(file: str):
    """Enhanced explain handler with beautiful output"""
    try:
        code = read_file(file)
        ui.print_code_block(code, "python", f"Code: {file}")
        
        explanation = explain_code(code, "python")
        
        ui.print_ai_response(explanation, "Code Explanation")
        
        return None
        
    except Exception as e:
        ui.print_error(f"Error explaining {file}: {e}")
        return None

def ask_handler(question: str):
    """Enhanced ask handler with streaming AI response"""
    try:
        # Use streaming for real-time word-by-word display
        stream = ask_stream(question)
        ui.print_ai_response_stream(stream, "AI Assistant Response")
        
        return None
        
    except Exception as e:
        ui.print_error(f"Error processing question: {e}")
        return None

def fix_handler(file: str):
    """Enhanced fix handler with beautiful output"""
    try:
        code = read_file(file)
        ui.print_code_block(code, "python", f"Original: {file}")
        
        # Check for issues first
        ok, messages = check_syntax_py(file)
        issues = ", ".join(messages) if messages else None
        
        new_code = fix_code(code, "python", issues)
        
        # Show diff if enabled
        if get_config_value('features.show_diffs', True):
            ui.print_diff(code, new_code, "Proposed Changes")
        
        # Show new code
        ui.print_code_block(new_code, "python", "Fixed Code")
        
        # Ask if user wants to apply
        if get_config_value('security.confirm_destructive', True):
            if ui.confirm("Apply these fixes to the file?", default=False):
                write_file(file, new_code)
                ui.print_success(f"✅ Fixes applied to {file}")
            else:
                ui.print_info("Changes not applied")
        
        return None, None, new_code
        
    except Exception as e:
        ui.print_error(f"Error fixing {file}: {e}")
        return None, None, None

def run_handler(command: str):
    """Enhanced run handler with beautiful output"""
    try:
        result = run_subprocess(command, timeout=120)
        
        exit_code = result.returncode
        stdout = result.stdout.decode()
        stderr = result.stderr.decode()
        
        # Show results
        if exit_code == 0:
            ui.print_success(f"✅ Command completed successfully", "Execution")
        else:
            ui.print_error(f"❌ Command failed with exit code {exit_code}", "Execution")
        
        if stdout:
            ui.print_code_block(stdout, "text", "Output")
        
        if stderr:
            ui.print_code_block(stderr, "text", "Errors")
        
        return exit_code, stdout, stderr
        
    except TimeoutError:
        ui.print_error("⏰ Command timed out after 120 seconds")
        return 124, "", "Timeout"
    except Exception as e:
        ui.print_error(f"Error executing command: {e}")
        return 1, "", str(e)

def generate_handler(template: str, name: str):
    """Enhanced generate handler with beautiful output"""
    try:
        if template == 'fastapi':
            template_path = os.path.join(os.path.dirname(__file__), 'resources', 'fastapi_template.py')
            code = read_file(template_path)
            
            os.makedirs(name, exist_ok=True)
            write_file(os.path.join(name, 'main.py'), code)
            
            ui.print_success(f"✅ FastAPI project '{name}' generated successfully!")
            ui.print_info(f"📁 Project created in: {os.path.abspath(name)}")
            ui.print_code_block(code, "python", "Generated main.py")
            
        else:
            ui.print_error(f"❌ Unknown template: {template}")
            ui.print_info("Available templates: fastapi")
            
    except Exception as e:
        ui.print_error(f"Error generating project: {e}")

def snippet_handler(action: str, name: str | None, content: str | None):
    """Enhanced snippet handler with beautiful output"""
    try:
        snippets_dir = os.path.join(CONFIG_DIR, 'snippets')
        os.makedirs(snippets_dir, exist_ok=True)
        
        if action == 'add':
            if name and content:
                write_file(os.path.join(snippets_dir, name), content)
                ui.print_success(f"✅ Snippet '{name}' added successfully!")
                return None
            else:
                ui.print_error("❌ Both name and content are required for adding snippets")
                return None
                
        elif action == 'list':
            snippets = os.listdir(snippets_dir)
            if snippets:
                data = []
                for snippet in snippets:
                    snippet_path = os.path.join(snippets_dir, snippet)
                    with open(snippet_path, 'r') as f:
                        content = f.read()
                    content_preview = f"{content[:50]}..." if len(content) > 50 else content
                    data.append({
                        "Name": snippet,
                        "Preview": content_preview
                    })
                ui.print_table(data, "Code Snippets")
            else:
                ui.print_info("No snippets found. Use 'snippet add <name> <content>' to add one.")
            return None
            
        elif action == 'remove':
            if name:
                snippet_path = os.path.join(snippets_dir, name)
                if os.path.exists(snippet_path):
                    os.remove(snippet_path)
                    ui.print_success(f"✅ Snippet '{name}' removed successfully!")
                else:
                    ui.print_error(f"❌ Snippet '{name}' not found")
                return None
            else:
                ui.print_error("❌ Name is required for removing snippets")
                return None
        else:
            ui.print_error(f"❌ Invalid snippet action: {action}")
            ui.print_info("Valid actions: add, list, remove")
            return None
            
    except Exception as e:
        ui.print_error(f"Error managing snippets: {e}")
        return None

def improve_handler(file: str):
    """New handler for code improvements"""
    try:
        code = read_file(file)
        ui.print_code_block(code, "python", f"Original: {file}")
        
        improvements = suggest_improvements(code, "python")
        
        ui.print_ai_response(improvements, "Code Improvement Suggestions")
        
        return None
        
    except Exception as e:
        ui.print_error(f"Error analyzing {file}: {e}")
        return None

def docs_handler(file: str):
    """New handler for documentation generation"""
    try:
        code = read_file(file)
        ui.print_code_block(code, "python", f"Code: {file}")
        
        documentation = generate_documentation(code, "python")
        
        ui.print_ai_response(documentation, "Generated Documentation")
        
        return None
        
    except Exception as e:
        ui.print_error(f"Error generating documentation for {file}: {e}")
        return None

def config_handler():
    """Show current configuration"""
    try:
        from core.config import CONFIG
        
        ui.print_info("⚙️ Current Configuration", "Settings")
        
        config_data = []
        for section, values in CONFIG.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    config_data.append({
                        "Section": section,
                        "Key": key,
                        "Value": str(value)
                    })
            else:
                config_data.append({
                    "Section": "root",
                    "Key": section,
                    "Value": str(values)
                })
        
        ui.print_table(config_data, "Configuration")
        return None
        
    except Exception as e:
        ui.print_error(f"Error showing configuration: {e}")
        return None

def status_handler():
    """Show system status and statistics"""
    try:
        import sqlite3
        from core.config import CACHE_DB, CONFIG_DIR
        
        ui.print_info("📊 System Status", "Statistics")
        
        # Cache statistics
        cache_count = 0
        if os.path.exists(CACHE_DB):
            conn = sqlite3.connect(CACHE_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cache")
            cache_count = cursor.fetchone()[0]
            conn.close()
        
        # File statistics
        config_size = 0
        if os.path.exists(CONFIG_DIR):
            for root, dirs, files in os.walk(CONFIG_DIR):
                for file in files:
                    config_size += os.path.getsize(os.path.join(root, file))
        
        status_data = [
            {"Metric": "Cached Responses", "Value": str(cache_count)},
            {"Metric": "Config Directory", "Value": CONFIG_DIR},
            {"Metric": "Config Size", "Value": f"{config_size / 1024:.1f} KB"},
            {"Metric": "API Provider", "Value": get_config_value('api.provider', 'metis')},
            {"Metric": "Model", "Value": get_config_value('api.model', 'kwaipilot/kat-coder-pro:free')},
            {"Metric": "Cache Enabled", "Value": str(get_config_value('features.cache_responses', True))},
            {"Metric": "Smart Completion", "Value": str(get_config_value('features.smart_completion', True))}
        ]
        
        ui.print_table(status_data, "System Status")
        return None
        
    except Exception as e:
        ui.print_error(f"Error showing status: {e}")
        return None