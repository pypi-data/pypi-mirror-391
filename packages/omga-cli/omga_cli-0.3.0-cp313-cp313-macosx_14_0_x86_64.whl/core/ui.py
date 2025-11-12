"""
Beautiful, professional UI components for omga-cli
Uses Rich library for enhanced formatting and streaming support
"""

from enum import Enum
from typing import Dict, Optional, List, Any, Iterator
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax
from rich.columns import Columns
from rich.align import Align
from rich.theme import Theme
from rich import box
import time
import sys
from core.logger import logger

class MessageType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

class OmgaUI:
    """Beautiful, professional UI manager for omga-cli with Rich"""
    
    def __init__(self):
        theme = Theme(
            {
                "content": "white",
                "accent": "cyan",
                "success": "bold green",
                "error": "bold red",
                "warning": "bold yellow",
                "info": "bold cyan",
                "debug": "dim white",
            }
        )
        # Create console with proper configuration
        # Detect terminal capabilities
        import os
        is_terminal = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        
        # Create console - Rich will auto-detect terminal capabilities
        self.console = Console(
            theme=theme,
            soft_wrap=True,
            highlight=False,
            legacy_windows=False,
            file=sys.stdout
        )
        
        # Use simpler output if terminal doesn't support colors well
        # or if we're in a restricted environment
        self.use_simple_output = (
            not is_terminal or
            os.getenv('NO_COLOR') or
            os.getenv('TERM') == 'dumb' or
            not self.console.is_terminal
        )
        self.icons = {
            MessageType.SUCCESS: "✅",
            MessageType.ERROR: "❌",
            MessageType.WARNING: "⚠️",
            MessageType.INFO: "ℹ️",
            MessageType.DEBUG: "🔍"
        }
        self.colors = {
            MessageType.SUCCESS: "green",
            MessageType.ERROR: "red",
            MessageType.WARNING: "yellow",
            MessageType.INFO: "cyan",
            MessageType.DEBUG: "white"
        }
        self.default_titles = {
            MessageType.SUCCESS: "Success",
            MessageType.ERROR: "Error",
            MessageType.WARNING: "Warning",
            MessageType.INFO: "Info",
            MessageType.DEBUG: "Debug",
        }
    
    def print_message(self, message: str, msg_type: MessageType = MessageType.INFO, 
                     title: Optional[str] = None, show_icon: bool = True):
        """Print beautiful message with clean formatting"""
        message = message or ""
        icon = self.icons.get(msg_type, "") if show_icon else ""
        heading_text = title or self.default_titles[msg_type]
        
        # Use simple, clean text output to avoid ANSI code issues
        # Format: [Icon] Title: Message
        print()  # Use print() directly to avoid Rich's ANSI codes
        if icon and not message.lstrip().startswith(icon):
            print(f"{icon} {heading_text}: {message}")
        else:
            print(f"{heading_text}: {message}")
        print()
        
        # Flush stdout to ensure output is displayed
        sys.stdout.flush()
    
    def print_success(self, message: str, title: str = "Success"):
        """Print success message with beautiful formatting"""
        self.print_message(message, MessageType.SUCCESS, title)
    
    def print_error(self, message: str, title: str = "Error"):
        """Print error message with beautiful formatting"""
        self.print_message(message, MessageType.ERROR, title)
    
    def print_warning(self, message: str, title: str = "Warning"):
        """Print warning message with beautiful formatting"""
        self.print_message(message, MessageType.WARNING, title)
    
    def print_info(self, message: str, title: str = "Info"):
        """Print info message with beautiful formatting"""
        self.print_message(message, MessageType.INFO, title)
    
    def print_code_block(self, code: str, language: str = "python", 
                        title: Optional[str] = None, show_line_numbers: bool = True):
        """Print formatted code block with syntax highlighting"""
        syntax = Syntax(code, language, line_numbers=show_line_numbers, theme="monokai")
        
        self.console.print()
        if title:
            panel = Panel(
                Align.left(syntax),
                title=f"[bold cyan]{title}[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
            self.console.print(panel)
        else:
            self.console.print(syntax)
        self.console.print()
    
    def print_table(self, data: List[Dict[str, Any]], title: str = "Results"):
        """Print data in a beautiful Rich table"""
        if not data:
            self.print_warning("No data to display")
            return
        
        table = Table(title=title, show_header=True, header_style="bold cyan", 
                     border_style="cyan", box=box.ROUNDED)
        
        # Add columns
        columns = list(data[0].keys())
        for col in columns:
            table.add_column(col, style="white")
        
        # Add rows
        for row in data:
            table.add_row(*[str(row[col]) for col in columns])
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def print_diff(self, old_text: str, new_text: str, title: str = "Changes"):
        """Print beautiful diff with Rich"""
        old_panel = Panel(
            Syntax(old_text, "python", theme="monokai"),
            title="[bold red]OLD[/bold red]",
            border_style="red",
            box=box.ROUNDED
        )
        
        new_panel = Panel(
            Syntax(new_text, "python", theme="monokai"),
            title="[bold green]NEW[/bold green]",
            border_style="green",
            box=box.ROUNDED
        )
        
        self.console.print()
        self.console.print(f"[bold cyan]{title}[/bold cyan]")
        self.console.print()
        self.console.print(Columns([old_panel, new_panel], equal=True))
        self.console.print()
    
    def print_help(self, commands: Dict[str, str]):
        """Print help in a beautiful Rich table"""
        table = Table(title="Available Commands", show_header=True, 
                     header_style="bold cyan", border_style="cyan", box=box.ROUNDED)
        table.add_column("Command", style="bold white", width=20)
        table.add_column("Description", style="white")
        
        for cmd, desc in commands.items():
            table.add_row(cmd, desc)
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def print_progress(self, message: str = "Processing..."):
        """Show progress indicator with spinner"""
        with self.console.status(f"[cyan]{message}[/cyan]", spinner="dots"):
            pass
    
    def print_spinner(self, message: str, duration: float = 2.0):
        """Show spinner for specified duration"""
        with self.console.status(f"[cyan]{message}[/cyan]", spinner="dots"):
            time.sleep(duration)
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Show confirmation prompt"""
        response = input(f"{message} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes']
    
    def prompt(self, message: str, default: str = "") -> str:
        """Show input prompt"""
        if default:
            response = input(f"{message} [{default}]: ").strip()
            return response if response else default
        else:
            return input(f"{message}: ").strip()
    
    def print_welcome(self):
        """Print beautiful welcome message"""
        welcome_text = Text()
        welcome_text.append("🚀 ", style="bold cyan")
        welcome_text.append("omga-cli", style="bold white")
        welcome_text.append(" - AI-Powered Development Assistant", style="white")
        
        subtitle = Text("Developed by ", style="dim white")
        subtitle.append("Pouria Hosseini", style="bold cyan")
        subtitle.append(" | ", style="dim white")
        subtitle.append("PouriaHosseini.news", style="cyan")
        
        panel = Panel(
            f"{welcome_text}\n\n{subtitle}\n\n[dim]Type 'help' for commands or 'exit' to quit[/dim]",
            title="[bold green]Welcome[/bold green]",
            border_style="green",
            padding=(1, 2),
            box=box.ROUNDED
        )
        
        self.console.print()
        self.console.print(panel)
        self.console.print()
    
    def print_feature_showcase(self):
        """Print beautiful feature showcase"""
        features = [
            ("🔍 Code Analysis", "Syntax checking, linting, error detection"),
            ("🤖 AI Assistant", "Smart explanations, fixes, and Q&A"),
            ("⚡ Fast Execution", "Safe command execution with progress"),
            ("🎨 Beautiful UI", "Rich, professional interface with streaming"),
            ("📚 Code Management", "Snippets, templates, scaffolding"),
            ("🔧 Auto-fixes", "AI-powered code improvements"),
            ("📊 Progress Tracking", "Real-time status and feedback"),
            ("🎯 Smart Completion", "AI-enhanced tab completion")
        ]
        
        table = Table(title="🌟 Feature Showcase", show_header=True,
                     header_style="bold cyan", border_style="cyan", box=box.ROUNDED)
        table.add_column("Feature", style="bold white", width=25)
        table.add_column("Description", style="white")
        
        for feature, desc in features:
            table.add_row(feature, desc)
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def print_status(self, status: str, details: Optional[str] = None):
        """Print status with beautiful formatting"""
        panel = Panel(
            f"[bold white]{status}[/bold white]\n{details or ''}",
            title="[bold cyan]📊 Status[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print()
        self.console.print(panel)
        self.console.print()
    
    def print_separator(self, char: str = "─", style: str = "dim white"):
        """Print visual separator"""
        self.console.print(f"[{style}]{char * 80}[/{style}]")
    
    def print_footer(self, message: str = "Happy coding! 🎉"):
        """Print beautiful footer message"""
        panel = Panel(
            f"[bold green]{message}[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 2)
        )
        self.console.print()
        self.console.print(panel)
        self.console.print()
    
    def print_ai_response(self, response: str, title: str = "AI Assistant Response"):
        """Print AI response in a beautiful, formatted way"""
        if not response or not response.strip():
            return
        
        # Format the response text simply and cleanly
        formatted_text = self._format_text(response.strip())
        
        # Always use simple, clean text output to avoid ANSI code issues
        # This ensures consistent output regardless of terminal capabilities
        print()  # Use print() directly to avoid Rich's ANSI codes
        print(f"🤖 {title}")
        print("=" * 70)
        print()
        print(formatted_text)
        print()
        print("-" * 70)
        print()
        
        # Flush stdout to ensure output is displayed
        sys.stdout.flush()
    
    def print_ai_response_stream(self, stream: Iterator[str], title: str = "AI Assistant Response"):
        """Print streaming AI response - collects all chunks first, then displays once"""
        # First, collect all chunks from the stream
        full_response = ""
        try:
            for chunk in stream:
                if chunk:
                    full_response += chunk
        except Exception as e:
            logger.error(f"Error collecting stream: {e}")
            self.print_error(f"Error receiving response: {e}")
            return ""
        
        # Clean and format the complete response
        if not full_response.strip():
            self.print_warning("Empty response received")
            return ""
        
        # Display the complete response once
        self.print_ai_response(full_response.strip(), title)
        return full_response.strip()

    def _build_message_lines(self, message: str, msg_type: Optional[MessageType]) -> Group:
        """Construct grouped Text lines for panels."""
        if not message:
            message = ""

        lines = message.strip("\n").splitlines() or [""]
        rendered_lines: List[Text] = []

        for index, line in enumerate(lines):
            text_line = Text(line, style="content")
            if index == 0 and msg_type:
                icon = self.icons.get(msg_type)
                color = self.colors.get(msg_type, "white")
                if icon:
                    text_line = Text.assemble((f"{icon} ", color), (line, "content"))
            rendered_lines.append(text_line)

        return Group(*rendered_lines)

    def _format_text(self, content: str) -> str:
        """Format text with simple markdown-like formatting."""
        if not content:
            return ""
        
        lines = content.split('\n')
        formatted_lines = []
        in_code_block = False
        code_lines = []
        
        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    if code_lines:
                        formatted_lines.append('')
                        formatted_lines.extend(code_lines)
                        formatted_lines.append('')
                    code_lines = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                continue
            
            if in_code_block:
                code_lines.append('    ' + line)
            else:
                # Handle headers
                if line.startswith('# '):
                    formatted_lines.append('')
                    formatted_lines.append(line[2:].strip().upper())
                    formatted_lines.append('-' * len(line[2:].strip()))
                elif line.startswith('## '):
                    formatted_lines.append('')
                    formatted_lines.append(line[3:].strip())
                    formatted_lines.append('─' * len(line[3:].strip()))
                # Handle lists
                elif line.strip().startswith('- ') or line.strip().startswith('* '):
                    formatted_lines.append('  • ' + line.strip()[2:])
                # Handle numbered lists
                elif line.strip() and line.strip()[0].isdigit() and '. ' in line.strip()[:4]:
                    formatted_lines.append('  ' + line.strip())
                # Regular text
                else:
                    formatted_lines.append(line)
        
        # Add any remaining code
        if code_lines:
            formatted_lines.append('')
            formatted_lines.extend(code_lines)
            formatted_lines.append('')
        
        # Clean up multiple blank lines
        result = []
        prev_blank = False
        for line in formatted_lines:
            is_blank = not line.strip()
            if is_blank and prev_blank:
                continue
            result.append(line)
            prev_blank = is_blank
        
        return '\n'.join(result).strip()
    
    def _render_markdown(self, content: str) -> Any:
        """Render markdown with graceful fallback to plain text."""
        cleaned = content.rstrip()
        if not cleaned:
            return Text("", style="content")

        try:
            return Markdown(cleaned, code_theme="monokai")
        except Exception:
            logger.debug("Markdown rendering failed, falling back to plain text", exc_info=True)
            return Text(cleaned, style="content")

# Global UI instance
ui = OmgaUI()