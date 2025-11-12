"""
Generate command - Convert RAG logs to training datasets.

The magic step that creates fine-tuning data from production logs.
"""

import click
import json
from pathlib import Path
from typing import Optional

from core.connectors import create_jsonl_connector, create_langsmith_connector
from core.filters import filter_logs
from core.converters.openai import convert_simple, convert_with_system_prompt, convert_with_context

from cli.ui import (
    console,
    success,
    error,
    warning,
    info,
    section,
    show_progress,
    spinner,
    show_next_steps
)


@click.command()
@click.argument('path', required=False, type=click.Path())
@click.option('--source', type=click.Choice(['jsonl', 'langsmith']), default='jsonl',
              help='Log source type (default: jsonl)')
@click.option('--project', type=str, help='LangSmith project name (required if source=langsmith)')
@click.option('--min-score', type=float, default=0.80,
              help='Minimum retrieval score for quality filter (default: 0.80)')
@click.option('--format', type=click.Choice(['simple', 'system-prompt', 'with-context']),
              default='simple',
              help='Conversion format (default: simple)')
@click.option('--system-prompt', type=str,
              help='Custom system prompt (for system-prompt format)')
@click.option('--output', '-o', type=click.Path(), default='training_data.jsonl',
              help='Output file path (default: training_data.jsonl)')
@click.option('--augment', is_flag=True,
              help='Generate query variations to expand dataset')
@click.option('--augment-factor', type=int, default=3,
              help='Number of variations per query (default: 3)')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed output')
def generate(
    path: Optional[str],
    source: str,
    project: Optional[str],
    min_score: float,
    format: str,
    system_prompt: Optional[str],
    output: str,
    augment: bool,
    augment_factor: int,
    verbose: bool
):
    """
    Generate training dataset from your RAG logs.

    \b
    Examples:
      # Basic usage
      distillery generate logs/*.jsonl

      # From LangSmith
      distillery generate --source langsmith --project my-rag-app

      # With system prompt
      distillery generate logs.jsonl --format system-prompt \\
          --system-prompt "You are a helpful customer support agent."

      # Include retrieved context
      distillery generate logs.jsonl --format with-context

      # Custom output location
      distillery generate logs.jsonl -o datasets/training_v1.jsonl

    \b
    What it does:
      1. Loads your RAG logs
      2. Filters high-quality examples
      3. Converts to OpenAI fine-tuning format
      4. Saves to JSONL file ready for upload
    """
    try:
        # Validate inputs
        if source == 'jsonl' and not path:
            error(
                "Path to log files is required",
                suggestions=[
                    "Provide a path: distillery generate logs/*.jsonl",
                    "Or use LangSmith: distillery generate --source langsmith --project my-project"
                ]
            )
            return

        if source == 'langsmith' and not project:
            error(
                "LangSmith project name is required",
                suggestions=[
                    "Specify project: distillery generate --source langsmith --project my-project"
                ]
            )
            return

        if format == 'system-prompt' and not system_prompt:
            warning(
                "No system prompt provided",
                detail="Using default: 'You are a helpful assistant.'"
            )
            system_prompt = "You are a helpful assistant."

        # Step 1: Connect to data source
        info("Generating training dataset...")
        console.print()

        connector = None
        if source == 'jsonl':
            with spinner("Connecting to log files..."):
                connector = create_jsonl_connector(path)
                if not connector.connect():
                    error(
                        f"Could not find log files at: {path}",
                        suggestions=[
                            "Check the path is correct",
                            "Ensure files have .jsonl extension"
                        ]
                    )
                    return
        else:  # langsmith
            with spinner("Connecting to LangSmith..."):
                try:
                    connector = create_langsmith_connector(project)
                    if not connector.connect():
                        error(f"Could not connect to LangSmith project: {project}")
                        return
                except Exception as e:
                    error(
                        f"LangSmith connection failed: {str(e)}",
                        suggestions=["Set LANGSMITH_API_KEY environment variable"]
                    )
                    return

        # Step 2: Load logs
        section("📥 Loading Logs")

        try:
            logs_list = []
            with spinner("Fetching logs..."):
                logs_list = list(connector.fetch_logs())

            if not logs_list:
                warning("No logs found")
                return

            success(f"Loaded {len(logs_list):,} logs")
        except Exception as e:
            error(f"Failed to load logs: {str(e)}")
            return

        # Step 3: Filter quality examples
        section("🔍 Filtering Quality Examples")

        with spinner(f"Applying quality filter (min score: {min_score})..."):
            filtered = filter_logs(logs_list, min_score=min_score)

        filter_pct = (len(filtered) / len(logs_list) * 100) if logs_list else 0
        success(f"Found {len(filtered):,} high-quality examples ({filter_pct:.0f}% of total)")

        if len(filtered) == 0:
            warning(
                "No examples passed quality filter",
                detail=f"Try lowering --min-score (currently {min_score})"
            )
            return

        if len(filtered) < 10:
            warning(
                "Very few examples",
                detail=f"Only {len(filtered)} examples. Fine-tuning works best with 50-100+."
            )

        # Step 4: Convert to training format
        section("🔄 Converting to Training Format")

        examples = []
        with spinner(f"Converting {len(filtered)} examples..."):
            if format == 'simple':
                examples = convert_simple(filtered)
            elif format == 'system-prompt':
                examples = convert_with_system_prompt(filtered, system_prompt)
            elif format == 'with-context':
                examples = convert_with_context(filtered)

        success(f"Converted {len(examples):,} training examples")

        # Show sample
        if verbose and examples:
            console.print()
            info("Sample training example:")
            console.print(json.dumps(
                {"messages": examples[0].messages},
                indent=2
            ))
            console.print()

        # Step 5: Augment dataset (optional)
        if augment:
            section("🌱 Augmenting Dataset")
            warning(
                "Data augmentation not yet implemented",
                detail="This feature will generate query variations to expand your dataset."
            )
            # TODO: Implement augmentation
            # augmented = augment_examples(examples, factor=augment_factor)
            # success(f"Generated {len(augmented):,} total examples ({augment_factor}x)")
            # examples = augmented

        # Step 6: Validate format
        with spinner("Validating OpenAI format..."):
            for i, example in enumerate(examples):
                # Basic validation
                if not example.messages:
                    error(f"Example {i} has no messages")
                    return

                for msg in example.messages:
                    if "role" not in msg or "content" not in msg:
                        error(f"Example {i} has invalid message format")
                        return

        success("All examples validated")

        # Step 7: Calculate stats
        total_tokens = sum(ex.estimate_tokens() for ex in examples)
        avg_tokens = total_tokens // len(examples) if examples else 0

        console.print()
        info(f"Total tokens: {total_tokens:,} (~${total_tokens / 1000 * 0.003:.2f} training cost)")
        info(f"Average tokens per example: {avg_tokens}")

        # Step 8: Save to file
        section("💾 Saving Dataset")

        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, 'w') as f:
                for example in examples:
                    f.write(json.dumps({"messages": example.messages}) + '\n')

            file_size = output_path.stat().st_size
            success(f"Saved to {output}")
            info(f"File size: {file_size / 1024:.1f} KB")
        except Exception as e:
            error(
                f"Failed to save file: {str(e)}",
                suggestions=[
                    "Check you have write permissions",
                    "Ensure the directory exists"
                ]
            )
            return

        # Step 9: Next steps
        console.print()
        show_next_steps([
            f"Review the output: head {output} | jq",
            f"Validate format: python -c \"import json; [json.loads(l) for l in open('{output}')]\"",
            f"Start training: distillery train {output}"
        ])

    except KeyboardInterrupt:
        console.print()
        warning("Generation cancelled by user")
    except Exception as e:
        error(
            f"Generation failed: {str(e)}",
            suggestions=[
                "Run with --verbose for more details",
                "Check your log format is correct"
            ]
        )
        if verbose:
            console.print_exception()
