from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import confirm, prompt
from core.config import HISTORY_FILE, CONFIG_DIR, get_config_value
from core.completer import OmgaCompleter
from core.commands import dispatch_command
from core.logger import logger
from core.ui import ui
import os
import sys

def run_shell():
    """Enhanced shell with beautiful interface"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        session = PromptSession(history=FileHistory(HISTORY_FILE))
        completer = OmgaCompleter()
        
        # Show minimal welcome message
        ui.print_welcome()
        
        command_count = 0
        
        while True:
            try:
                # Get user input (with patch_stdout only for the prompt)
                with patch_stdout():
                    command_count += 1
                    prompt_text = "omga-cli> "
                    text = session.prompt(prompt_text, completer=completer)
                
                # Process command outside of patch_stdout to avoid ANSI code issues
                if text.strip().lower() in ['exit', 'quit', 'bye']:
                    ui.print_info("👋 Goodbye! Happy coding!")
                    break
                
                if text.strip():
                    dispatch_command(text)
                        
            except KeyboardInterrupt:
                ui.print_warning("Input cleared (Ctrl-C). Type 'exit' to quit.")
            except EOFError:
                ui.print_info("👋 Goodbye! Happy coding!")
                break
            except Exception as e:
                logger.error(f"Shell error: {e}")
                ui.print_error(f"Shell error: {e}")
                    
    except Exception as e:
        ui.print_error(f"Failed to start shell: {e}")
        sys.exit(1)