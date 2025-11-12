"""
Distillery CLI - Main entry point.

Beautiful command-line interface for converting RAG logs to fine-tuning datasets.
"""

import click
from cli.ui import welcome
from cli.commands import analyze, generate, train


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="distillery")
@click.pass_context
def cli(ctx):
    """
    Distillery - Convert RAG logs into fine-tuning datasets.

    \b
    Commands:
      analyze   - Analyze your RAG logs and see if fine-tuning makes sense
      generate  - Generate training dataset from your logs
      train     - Upload and start fine-tuning

    \b
    Quick Start:
      distillery analyze logs/*.jsonl
      distillery generate logs/*.jsonl
      distillery train training_data.jsonl

    \b
    Learn more: https://docs.distillery.ai
    """
    # If no command is provided, show welcome screen
    if ctx.invoked_subcommand is None:
        welcome()


# Register commands
cli.add_command(analyze)
cli.add_command(generate)
cli.add_command(train)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
