"""
Analyze command - The "hook" that shows value immediately.

Analyzes RAG logs and shows if fine-tuning makes sense.
"""

import click
from pathlib import Path
from typing import Optional
from datetime import datetime

from core.connectors import create_jsonl_connector, create_langsmith_connector
from core.analyzers.stats import analyze_logs
from core.filters import filter_logs
from utils.cost_calculator import CostCalculator, estimate_savings

from cli.ui import (
    console,
    success,
    error,
    warning,
    info,
    section,
    show_progress,
    spinner,
    create_stats_table,
    create_quality_distribution_table,
    create_cost_table,
    show_cost_savings,
    show_recommendation,
    show_next_steps,
    print_summary_panel
)


@click.command()
@click.argument('path', required=False, type=click.Path())
@click.option('--source', type=click.Choice(['jsonl', 'langsmith']), default='jsonl',
              help='Log source type (default: jsonl)')
@click.option('--project', type=str, help='LangSmith project name (required if source=langsmith)')
@click.option('--min-score', type=float, default=0.80,
              help='Minimum retrieval score for quality filter (default: 0.80)')
@click.option('--monthly-queries', type=int, default=None,
              help='Estimated monthly query volume (defaults to analyzing logs)')
@click.option('--model', type=str, default='gpt-4o-mini',
              help='OpenAI model to use (default: gpt-4o-mini)')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed analysis output')
@click.option('--output', '-o', type=click.Path(),
              help='Save detailed report to JSON file')
def analyze(
    path: Optional[str],
    source: str,
    project: Optional[str],
    min_score: float,
    monthly_queries: Optional[int],
    model: str,
    verbose: bool,
    output: Optional[str]
):
    """
    Analyze your RAG logs and see if fine-tuning makes sense.

    \b
    Examples:
      # Analyze local logs
      distillery analyze logs/*.jsonl

      # From LangSmith
      distillery analyze --source langsmith --project my-rag-app

      # Stricter quality filter
      distillery analyze logs.jsonl --min-score 0.90

      # With custom query volume
      distillery analyze logs.jsonl --monthly-queries 100000

    \b
    What it does:
      1. Loads your RAG logs
      2. Analyzes quality (retrieval scores, feedback)
      3. Estimates cost savings from fine-tuning
      4. Recommends next steps
    """
    try:
        # Validate inputs
        if source == 'jsonl' and not path:
            error(
                "Path to log files is required",
                suggestions=[
                    "Provide a path to your logs: distillery analyze logs/*.jsonl",
                    "Or use LangSmith: distillery analyze --source langsmith --project my-project"
                ]
            )
            return

        if source == 'langsmith' and not project:
            error(
                "LangSmith project name is required",
                suggestions=[
                    "Specify your project: distillery analyze --source langsmith --project my-project",
                    "Find your projects: https://smith.langchain.com/"
                ]
            )
            return

        # Step 1: Connect to data source
        info("Analyzing your RAG logs...")
        console.print()

        connector = None
        if source == 'jsonl':
            with spinner("Connecting to log files..."):
                connector = create_jsonl_connector(path)
                if not connector.connect():
                    error(
                        f"Could not find any log files at: {path}",
                        suggestions=[
                            f"Check the path exists: ls {Path(path).parent}",
                            "Ensure files have .jsonl extension",
                            "Use glob patterns: logs/**/*.jsonl"
                        ],
                        help_url="https://docs.distillery.ai/connectors/jsonl"
                    )
                    return
        else:  # langsmith
            with spinner("Connecting to LangSmith..."):
                try:
                    connector = create_langsmith_connector(project)
                    if not connector.connect():
                        error(
                            f"Could not connect to LangSmith project: {project}",
                            suggestions=[
                                "Check your LANGSMITH_API_KEY is set",
                                "Verify the project name is correct",
                                "Check project exists: https://smith.langchain.com/"
                            ],
                            help_url="https://docs.distillery.ai/connectors/langsmith"
                        )
                        return
                except Exception as e:
                    error(
                        f"LangSmith connection failed: {str(e)}",
                        suggestions=[
                            "Set LANGSMITH_API_KEY environment variable",
                            "Install langsmith: pip install langsmith"
                        ]
                    )
                    return

        # Step 2: Load logs
        section("📥 Loading Logs")

        try:
            logs_list = []
            with spinner("Fetching logs..."):
                logs_list = list(connector.fetch_logs())

            if not logs_list:
                warning(
                    "No logs found",
                    detail="The data source returned no logs. Check your filters or date range."
                )
                return

            success(f"Loaded {len(logs_list):,} logs")
        except Exception as e:
            error(
                f"Failed to load logs: {str(e)}",
                suggestions=[
                    "Check the file format is correct",
                    "Ensure logs contain required fields (query, response, retrieved_chunks)"
                ]
            )
            return

        # Step 3: Analyze logs
        section("📊 Quality Analysis")

        with spinner("Analyzing quality metrics..."):
            stats = analyze_logs(logs_list)

        if verbose:
            # Show detailed stats table
            console.print(create_stats_table(stats))
            console.print()
            console.print(create_quality_distribution_table(stats))
        else:
            # Show quick summary
            quality_pct = (stats.successful_queries / stats.total_queries * 100) if stats.total_queries > 0 else 0
            info(f"Quality: {quality_pct:.0f}% successful | Avg score: {stats.avg_retrieval_score:.2f}")

        # Step 4: Filter high-quality examples
        with spinner("Filtering high-quality examples..."):
            filtered = filter_logs(logs_list, min_score=min_score)

        filter_pct = (len(filtered) / len(logs_list) * 100) if logs_list else 0
        info(f"Found {len(filtered):,} high-quality examples ({filter_pct:.0f}% of total)")

        if len(filtered) == 0:
            warning(
                "No examples passed quality filter",
                detail=f"Try lowering --min-score (currently {min_score})"
            )
            return

        if len(filtered) < 10:
            warning(
                "Very few examples for training",
                detail=f"Only {len(filtered)} examples. Fine-tuning typically needs 50-100+ examples."
            )

        # Step 5: Calculate costs
        section("💰 Cost Analysis")

        with spinner("Calculating ROI..."):
            # Estimate monthly queries if not provided
            if monthly_queries is None:
                # Estimate from log data if we have date range
                if stats.date_range:
                    days = (stats.date_range[1] - stats.date_range[0]).days
                    if days > 0:
                        monthly_queries = int((stats.total_queries / days) * 30)
                    else:
                        monthly_queries = stats.total_queries * 30  # Assume daily logs
                else:
                    monthly_queries = stats.total_queries * 30  # Assume daily logs

                info(f"Estimated monthly volume: {monthly_queries:,} queries")

            # Calculate costs
            # Convert filtered logs to training examples for cost calculation
            from core.converters.openai import convert_simple
            training_examples = convert_simple(filtered)

            comparison = estimate_savings(
                logs=logs_list,
                training_examples=training_examples,
                monthly_queries=monthly_queries,
                model=model
            )

        if verbose:
            console.print(create_cost_table(comparison))
        else:
            # Quick summary
            show_cost_savings(
                monthly_rag_cost=comparison.monthly_rag_cost,
                monthly_finetuned_cost=comparison.monthly_finetuned_cost,
                monthly_savings=comparison.monthly_savings,
                training_cost=comparison.training_cost,
                breakeven_months=comparison.breakeven_months
            )

        # Step 6: Show recommendation
        should_finetune = (
            len(filtered) >= 50 and  # Enough examples
            filter_pct >= 70 and  # Good quality data
            comparison.monthly_savings > 0 and  # Cost savings
            comparison.breakeven_months < 2  # Fast break-even
        )

        breakeven_days = int(comparison.breakeven_months * 30) if comparison.breakeven_months < float('inf') else 999

        show_recommendation(
            should_finetune=should_finetune,
            quality_pct=filter_pct,
            monthly_savings=comparison.monthly_savings if comparison.monthly_savings > 0 else 0,
            breakeven_days=breakeven_days
        )

        # Step 7: Next steps
        if should_finetune:
            generate_cmd = path if path else f"--source langsmith --project {project}"
            show_next_steps([
                f"Generate training data: distillery generate {generate_cmd}",
                "Review the output: head training_data.jsonl | jq",
                "Start training: distillery train training_data.jsonl"
            ])
        else:
            if len(filtered) < 50:
                show_next_steps([
                    "Collect more production data (need 50-100+ examples)",
                    "Run analyze again when you have more logs",
                    "Consider improving your RAG system first"
                ])
            elif filter_pct < 70:
                show_next_steps([
                    "Improve retrieval quality (currently {:.0f}%)".format(filter_pct),
                    "Check retrieval strategy and embeddings",
                    "Review low-scoring queries: distillery analyze --verbose"
                ])
            else:
                generate_cmd = path if path else f"--source langsmith --project {project}"
                show_next_steps([
                    "Wait for more query volume (need higher scale for ROI)",
                    "Re-run when you reach ~10,000 queries/month",
                    f"Or proceed anyway: distillery generate {generate_cmd}"
                ])

        # Step 8: Save report if requested
        if output:
            import json
            report = {
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "path": path,
                "project": project,
                "stats": {
                    "total_queries": stats.total_queries,
                    "successful_queries": stats.successful_queries,
                    "avg_retrieval_score": stats.avg_retrieval_score,
                    "score_distribution": stats.score_distribution,
                    "feedback_counts": stats.feedback_counts,
                    "topic_distribution": dict(sorted(stats.topic_distribution.items(), key=lambda x: x[1], reverse=True)[:10]) if stats.topic_distribution else {}
                },
                "filtering": {
                    "min_score": min_score,
                    "filtered_count": len(filtered),
                    "filter_rate": filter_pct
                },
                "costs": {
                    "rag_cost_per_query": comparison.rag_cost_per_query,
                    "finetuned_cost_per_query": comparison.finetuned_cost_per_query,
                    "monthly_rag_cost": comparison.monthly_rag_cost,
                    "monthly_finetuned_cost": comparison.monthly_finetuned_cost,
                    "monthly_savings": comparison.monthly_savings,
                    "training_cost": comparison.training_cost,
                    "breakeven_months": comparison.breakeven_months,
                    "monthly_queries": monthly_queries
                },
                "recommendation": {
                    "should_finetune": should_finetune,
                    "quality_pct": filter_pct,
                    "monthly_savings": comparison.monthly_savings,
                    "breakeven_days": breakeven_days
                }
            }

            with open(output, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            success(f"Report saved to {output}")

    except KeyboardInterrupt:
        console.print()
        warning("Analysis cancelled by user")
    except Exception as e:
        error(
            f"Analysis failed: {str(e)}",
            suggestions=[
                "Run with --verbose for more details",
                "Check your log format matches the schema",
                "Report issue: https://github.com/yourusername/distillery/issues"
            ]
        )
        if verbose:
            console.print_exception()
