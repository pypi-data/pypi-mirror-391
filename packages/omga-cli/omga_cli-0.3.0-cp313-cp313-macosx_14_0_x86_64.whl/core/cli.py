import sys
import click
from core.shell import run_shell
from core.commands import (
    check_handler, explain_handler, ask_handler, fix_handler,
    run_handler, generate_handler, snippet_handler, improve_handler,
    docs_handler, config_handler, status_handler
)
from core.ui import ui

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        run_shell()
    else:
        pass  # Subcommand will handle

@main.command()
@click.argument('file', type=click.Path(exists=True))
def check(file):
    """Check syntax and linting of a Python file"""
    check_handler(file)

@main.command()
@click.argument('file', type=click.Path(exists=True))
def explain(file):
    """Get detailed AI explanation of code"""
    explain_handler(file)

@main.command()
@click.argument('question', nargs=-1)
def ask(question):
    """Ask any question to the AI"""
    question = ' '.join(question)
    ask_handler(question)

@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--apply', is_flag=True, help='Apply fixes to file')
def fix(file, apply):
    """Suggest and apply fixes for code issues"""
    fix_handler(file)

@main.command()
@click.argument('file', type=click.Path(exists=True))
def improve(file):
    """Get suggestions for code improvements"""
    improve_handler(file)

@main.command()
@click.argument('file', type=click.Path(exists=True))
def docs(file):
    """Generate documentation for code"""
    docs_handler(file)

@main.command()
@click.argument('command', nargs=-1)
def run(command):
    """Run a shell command safely"""
    command = ' '.join(command)
    exit_code, stdout, stderr = run_handler(command)
    sys.exit(exit_code)

@main.command('generate')
@click.argument('type')
@click.argument('template')
@click.argument('name')
def generate_cmd(type, template, name):
    """Generate a new project from template"""
    if type != 'project':
        ui.print_error("Only 'project' type is supported.")
        sys.exit(1)
    generate_handler(template, name)

@main.command('snippet')
@click.argument('action', type=click.Choice(['add', 'list', 'remove']))
@click.argument('name', required=False)
@click.argument('content', required=False, nargs=-1)
def snippet_cmd(action, name, content):
    """Manage code snippets"""
    content = ' '.join(content) if content else None
    snippet_handler(action, name, content)

@main.command()
def config():
    """Show current configuration"""
    config_handler()

@main.command()
def status():
    """Show system status and statistics"""
    status_handler()

if __name__ == '__main__':
    main()