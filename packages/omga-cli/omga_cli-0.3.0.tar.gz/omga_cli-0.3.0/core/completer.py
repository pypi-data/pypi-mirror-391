from prompt_toolkit.completion import Completer, Completion
from threading import Thread, Lock
import time
import os
import glob
from core.ai import ask
from core.cache_db import get, set_
from core.logger import logger
from core.config import get_config_value

class OmgaCompleter(Completer):
    def __init__(self):
        self.static_suggestions = [
            'check', 'explain', 'ask', 'fix', 'improve', 'docs', 'run', 
            'generate', 'project', 'snippet', 'add', 'list', 'remove',
            'config', 'status', 'help', 'exit', 'quit'
        ]
        self.cache_lock = Lock()
        self.ai_cache = {}  # In-memory for speed, backed by db
        self.load_cache()

    def load_cache(self):
        """Load cached completions"""
        for key in self.static_suggestions:
            cached = get(f"completion_{key}")
            if cached:
                self.ai_cache[key] = cached.split(',')

    def get_completions(self, document, complete_event):
        """Get completions with enhanced logic"""
        text = document.text_before_cursor
        words = text.split()
        
        if not words:
            # Show all commands when starting
            for cmd in self.static_suggestions:
                yield Completion(cmd, start_position=0, display_meta="Command")
            return

        partial = words[-1]
        context = words[:-1] if len(words) > 1 else []
        
        # Command completions
        if len(words) == 1:
            for cmd in self.static_suggestions:
                if cmd.startswith(partial):
                    meta = self._get_command_meta(cmd)
                    yield Completion(cmd, start_position=-len(partial), display_meta=meta)
        
        # File completions for file-based commands
        elif words[0] in ['check', 'explain', 'fix', 'improve', 'docs']:
            for file_path in self._get_file_completions(partial):
                yield Completion(file_path, start_position=-len(partial), display_meta="File")
        
        # Snippet completions
        elif words[0] == 'snippet' and len(words) >= 2:
            if words[1] in ['remove'] and len(words) == 3:
                for snippet in self._get_snippet_completions(partial):
                    yield Completion(snippet, start_position=-len(partial), display_meta="Snippet")
        
        # AI-powered completions (if enabled)
        if get_config_value('features.smart_completion', True):
            self._fetch_ai_completions(partial, context)

    def _get_command_meta(self, cmd):
        """Get metadata for commands"""
        meta_map = {
            'check': 'Check syntax and linting',
            'explain': 'Get AI explanation',
            'ask': 'Ask AI questions',
            'fix': 'Fix code issues',
            'improve': 'Get improvement suggestions',
            'docs': 'Generate documentation',
            'run': 'Run shell commands',
            'generate': 'Generate projects',
            'snippet': 'Manage code snippets',
            'config': 'Show configuration',
            'status': 'Show system status',
            'help': 'Show help',
            'exit': 'Exit shell'
        }
        return meta_map.get(cmd, "Command")

    def _get_file_completions(self, partial):
        """Get file completions"""
        if not partial:
            return []
        
        # Handle relative paths
        if '/' in partial:
            dir_path = os.path.dirname(partial)
            pattern = os.path.basename(partial) + '*'
            search_path = os.path.join(dir_path, pattern)
        else:
            search_path = partial + '*'
        
        try:
            # Get Python files
            py_files = glob.glob(search_path + '.py')
            # Get all files
            all_files = glob.glob(search_path)
            
            # Combine and deduplicate
            files = list(set(py_files + all_files))
            return files[:10]  # Limit to 10 suggestions
        except:
            return []

    def _get_snippet_completions(self, partial):
        """Get snippet completions"""
        try:
            from core.config import CONFIG_DIR
            snippets_dir = os.path.join(CONFIG_DIR, 'snippets')
            if os.path.exists(snippets_dir):
                snippets = os.listdir(snippets_dir)
                return [s for s in snippets if s.startswith(partial)]
        except:
            pass
        return []

    def _fetch_ai_completions(self, partial, context):
        """Fetch AI-powered completions in background"""
        if partial not in self.ai_cache and len(partial) > 2:
            Thread(target=self.fetch_ai_completions_worker, args=(partial, context)).start()

    def fetch_ai_completions_worker(self, partial, context):
        """Worker thread for AI completions"""
        try:
            context_str = ' '.join(context) if context else ""
            prompt = f"""
            Suggest up to 5 completions for this CLI command context:
            Context: {context_str}
            Partial: {partial}
            
            Return only the completion suggestions, one per line, no explanations.
            """
            
            response = ask(prompt)
            suggestions = [line.strip() for line in response.strip().split('\n') if line.strip()][:5]
            
            with self.cache_lock:
                self.ai_cache[partial] = suggestions
                set_(f"completion_{partial}", ','.join(suggestions))
                
        except Exception as e:
            logger.error(f"AI completion error: {e}")