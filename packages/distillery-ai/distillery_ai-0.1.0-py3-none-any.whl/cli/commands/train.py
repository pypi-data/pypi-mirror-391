"""
Train command - Upload and start OpenAI fine-tuning.

The payoff - kicks off the fine-tuning job.
"""

import click
import json
import time
from pathlib import Path
from typing import Optional

from cli.ui import (
    console,
    success,
    error,
    warning,
    info,
    section,
    spinner,
    show_next_steps
)


@click.command()
@click.argument('training_file', type=click.Path(exists=True))
@click.option('--model', type=str, default='gpt-4o-mini-2024-07-18',
              help='Base model to fine-tune (default: gpt-4o-mini-2024-07-18)')
@click.option('--suffix', type=str,
              help='Custom suffix for the fine-tuned model name')
@click.option('--validation-file', type=click.Path(exists=True),
              help='Optional validation dataset')
@click.option('--epochs', type=int,
              help='Number of training epochs (default: auto)')
@click.option('--batch-size', type=int,
              help='Batch size for training (default: auto)')
@click.option('--learning-rate-multiplier', type=float,
              help='Learning rate multiplier (default: auto)')
@click.option('--wait', is_flag=True,
              help='Wait for training to complete')
@click.option('--api-key', type=str,
              help='OpenAI API key (or set OPENAI_API_KEY env var)')
def train(
    training_file: str,
    model: str,
    suffix: Optional[str],
    validation_file: Optional[str],
    epochs: Optional[int],
    batch_size: Optional[int],
    learning_rate_multiplier: Optional[float],
    wait: bool,
    api_key: Optional[str]
):
    """
    Upload training data and start OpenAI fine-tuning.

    \b
    Examples:
      # Basic usage
      distillery train training_data.jsonl

      # With custom model name
      distillery train training_data.jsonl --suffix "customer-support-v1"

      # Wait for completion
      distillery train training_data.jsonl --wait

      # With validation set
      distillery train training_data.jsonl --validation-file validation.jsonl

    \b
    What it does:
      1. Validates training data format
      2. Uploads to OpenAI
      3. Starts fine-tuning job
      4. Monitors progress (if --wait)
      5. Returns fine-tuned model ID
    """
    try:
        # Step 1: Check API key
        import os
        api_key = api_key or os.getenv('OPENAI_API_KEY')

        if not api_key:
            error(
                "OpenAI API key not found",
                suggestions=[
                    "Set OPENAI_API_KEY environment variable",
                    "Or pass --api-key flag",
                    "Get key: https://platform.openai.com/api-keys"
                ]
            )
            return

        # Import OpenAI client
        try:
            from openai import OpenAI
        except ImportError:
            error(
                "OpenAI library not installed",
                suggestions=[
                    "Install: pip install openai",
                    "Or: pip install distillery-ai[full]"
                ]
            )
            return

        client = OpenAI(api_key=api_key)

        info("Starting fine-tuning workflow...")
        console.print()

        # Step 2: Validate training file
        section("✅ Validating Training Data")

        training_path = Path(training_file)
        file_size = training_path.stat().st_size

        info(f"File: {training_file}")
        info(f"Size: {file_size / 1024:.1f} KB")

        # Load and validate
        try:
            with open(training_file, 'r') as f:
                examples = [json.loads(line) for line in f]

            if not examples:
                error("Training file is empty")
                return

            # Validate format
            for i, ex in enumerate(examples):
                if "messages" not in ex:
                    error(f"Example {i} missing 'messages' field")
                    return

                for msg in ex["messages"]:
                    if "role" not in msg or "content" not in msg:
                        error(f"Example {i} has invalid message format")
                        return

            success(f"Validated {len(examples):,} training examples")
        except json.JSONDecodeError as e:
            error(
                f"Invalid JSON format: {str(e)}",
                suggestions=[
                    "Check file is valid JSONL (one JSON object per line)",
                    "Regenerate with: distillery generate"
                ]
            )
            return

        # OpenAI requirements
        if len(examples) < 10:
            warning(
                "Very few training examples",
                detail=f"OpenAI recommends at least 10 examples. You have {len(examples)}."
            )

        # Step 3: Upload training file
        section("📤 Uploading to OpenAI")

        try:
            with spinner("Uploading training data..."):
                with open(training_file, 'rb') as f:
                    training_file_obj = client.files.create(
                        file=f,
                        purpose='fine-tune'
                    )

            success(f"Uploaded training file: {training_file_obj.id}")
        except Exception as e:
            error(
                f"Upload failed: {str(e)}",
                suggestions=[
                    "Check your API key is valid",
                    "Verify your OpenAI account has access",
                    "Check file size limits"
                ]
            )
            return

        # Step 4: Upload validation file (if provided)
        validation_file_obj = None
        if validation_file:
            try:
                with spinner("Uploading validation data..."):
                    with open(validation_file, 'rb') as f:
                        validation_file_obj = client.files.create(
                            file=f,
                            purpose='fine-tune'
                        )

                success(f"Uploaded validation file: {validation_file_obj.id}")
            except Exception as e:
                warning(f"Validation file upload failed: {str(e)}")

        # Step 5: Create fine-tuning job
        section("🚀 Starting Fine-Tuning")

        # Build job parameters
        job_params = {
            "training_file": training_file_obj.id,
            "model": model,
        }

        if validation_file_obj:
            job_params["validation_file"] = validation_file_obj.id

        if suffix:
            job_params["suffix"] = suffix

        if epochs:
            job_params["hyperparameters"] = {"n_epochs": epochs}

        # Add other hyperparameters if specified
        if batch_size or learning_rate_multiplier:
            if "hyperparameters" not in job_params:
                job_params["hyperparameters"] = {}
            if batch_size:
                job_params["hyperparameters"]["batch_size"] = batch_size
            if learning_rate_multiplier:
                job_params["hyperparameters"]["learning_rate_multiplier"] = learning_rate_multiplier

        try:
            with spinner("Creating fine-tuning job..."):
                job = client.fine_tuning.jobs.create(**job_params)

            success(f"Fine-tuning job created: {job.id}")
            info(f"Base model: {job.model}")
            if suffix:
                info(f"Model suffix: {suffix}")
        except Exception as e:
            error(
                f"Failed to create fine-tuning job: {str(e)}",
                suggestions=[
                    "Check you have access to the model",
                    "Verify your OpenAI subscription",
                    "Check training data format"
                ]
            )
            return

        # Step 6: Monitor progress (if --wait)
        if wait:
            section("⏳ Monitoring Training Progress")

            info("Waiting for training to complete...")
            info("This may take 10-30 minutes depending on dataset size.")
            console.print()

            last_status = None
            while True:
                try:
                    job = client.fine_tuning.jobs.retrieve(job.id)

                    if job.status != last_status:
                        last_status = job.status

                        if job.status == "validating_files":
                            info("Status: Validating files...")
                        elif job.status == "queued":
                            info("Status: Queued for training...")
                        elif job.status == "running":
                            info("Status: Training in progress...")
                        elif job.status == "succeeded":
                            console.print()
                            success("Training completed!")
                            success(f"Fine-tuned model: {job.fine_tuned_model}")
                            break
                        elif job.status == "failed":
                            console.print()
                            error(
                                f"Training failed: {job.error.message if job.error else 'Unknown error'}",
                                suggestions=[
                                    "Check the training data format",
                                    "Review OpenAI dashboard for details",
                                    f"Job ID: {job.id}"
                                ]
                            )
                            return
                        elif job.status == "cancelled":
                            console.print()
                            warning("Training was cancelled")
                            return

                    time.sleep(10)  # Poll every 10 seconds

                except KeyboardInterrupt:
                    console.print()
                    warning("Monitoring stopped (training continues in background)")
                    info(f"Check status: distillery status {job.id}")
                    return
                except Exception as e:
                    error(f"Failed to check status: {str(e)}")
                    return

            # Show final stats
            if job.trained_tokens:
                info(f"Tokens trained: {job.trained_tokens:,}")

            console.print()
            show_next_steps([
                f"Test your model: Use model ID '{job.fine_tuned_model}' in your API calls",
                "Monitor usage: https://platform.openai.com/usage",
                "Compare costs: distillery compare --model " + job.fine_tuned_model
            ])

        else:
            # Not waiting - show how to check status
            console.print()
            info("Training started in background.")
            info(f"Job ID: {job.id}")

            console.print()
            show_next_steps([
                f"Check status: distillery status {job.id}",
                "Or view in dashboard: https://platform.openai.com/finetune",
                "Get job info via API: client.fine_tuning.jobs.retrieve('" + job.id + "')"
            ])

    except KeyboardInterrupt:
        console.print()
        warning("Training setup cancelled by user")
    except Exception as e:
        error(
            f"Training failed: {str(e)}",
            suggestions=[
                "Check your OpenAI API key is valid",
                "Verify training data format",
                "Review OpenAI documentation"
            ]
        )
        console.print_exception()
