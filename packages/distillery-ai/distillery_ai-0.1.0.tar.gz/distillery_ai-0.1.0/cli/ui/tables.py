"""
Table formatting for Distillery CLI.

Provides beautiful tables for statistics and cost comparisons using rich.
"""

from typing import Optional
from rich.table import Table
from rich.console import Console
from rich.text import Text
from core.models import DatasetStats, CostComparison

console = Console()


def create_stats_table(stats: DatasetStats) -> Table:
    """
    Create a formatted table showing dataset statistics.

    Args:
        stats: DatasetStats object with analysis results

    Returns:
        Rich Table object ready to print

    Example:
        >>> table = create_stats_table(stats)
        >>> console.print(table)
    """
    table = Table(
        title="📊 Dataset Statistics",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title_style="bold white"
    )

    table.add_column("Metric", style="cyan", justify="left")
    table.add_column("Value", style="white", justify="right")
    table.add_column("Details", style="dim", justify="left")

    # Overview
    table.add_row(
        "Total Queries",
        str(stats.total_queries),
        f"From {stats.date_range[0].strftime('%b %d')} to {stats.date_range[1].strftime('%b %d, %Y')}" if stats.date_range else ""
    )

    # Quality metrics
    success_rate = (stats.successful_queries / stats.total_queries * 100) if stats.total_queries > 0 else 0
    table.add_row(
        "Success Rate",
        f"{success_rate:.1f}%",
        f"{stats.successful_queries:,} successful"
    )

    table.add_row(
        "Avg Retrieval Score",
        f"{stats.avg_retrieval_score:.2f}",
        _create_score_bar(stats.avg_retrieval_score)
    )

    # Feedback
    if stats.feedback_counts:
        thumbs_up = stats.feedback_counts.get("thumbs_up", 0)
        thumbs_down = stats.feedback_counts.get("thumbs_down", 0)
        total_feedback = thumbs_up + thumbs_down

        if total_feedback > 0:
            positive_rate = (thumbs_up / total_feedback * 100) if total_feedback > 0 else 0
            table.add_row(
                "User Feedback",
                f"{positive_rate:.0f}% positive",
                f"{thumbs_up} 👍  {thumbs_down} 👎"
            )

    # Top topics
    if stats.topic_distribution:
        top_topics = sorted(stats.topic_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        topics_str = ", ".join([f"{topic} ({count})" for topic, count in top_topics])
        table.add_row(
            "Top Topics",
            f"{len(stats.topic_distribution)} found",
            topics_str
        )

    return table


def create_quality_distribution_table(stats: DatasetStats) -> Table:
    """
    Create a table showing quality score distribution with visual bars.

    Args:
        stats: DatasetStats object

    Returns:
        Rich Table object

    Example:
        >>> table = create_quality_distribution_table(stats)
        >>> console.print(table)

        Quality Distribution
        ┌─────────────┬───────┬────────────┬──────────────────────────┐
        │ Score Range │ Count │ Percentage │ Visual                   │
        ├─────────────┼───────┼────────────┼──────────────────────────┤
        │ 0.9 - 1.0   │   542 │     44.0%  │ ████████████████████████ │
        │ 0.8 - 0.9   │   488 │     39.5%  │ ███████████████████      │
        └─────────────┴───────┴────────────┴──────────────────────────┘
    """
    table = Table(
        title="Quality Distribution",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title_style="bold white"
    )

    table.add_column("Score Range", style="cyan", justify="left")
    table.add_column("Count", style="white", justify="right")
    table.add_column("Percentage", style="white", justify="right")
    table.add_column("Visual", style="", justify="left")

    # Define score ranges
    score_ranges = [
        ("0.9 - 1.0", 0.9, 1.0, "green"),
        ("0.8 - 0.9", 0.8, 0.9, "green"),
        ("0.7 - 0.8", 0.7, 0.8, "yellow"),
        ("0.6 - 0.7", 0.6, 0.7, "yellow"),
        ("0.0 - 0.6", 0.0, 0.6, "red"),
    ]

    total = stats.total_queries
    if total == 0:
        return table

    for label, low, high, color in score_ranges:
        # Count logs in this range
        count = stats.score_distribution.get(label, 0)
        if count == 0:
            continue

        percentage = (count / total) * 100
        bar_length = int(percentage / 2)  # Scale to fit
        bar = "█" * bar_length

        table.add_row(
            label,
            f"{count:,}",
            f"{percentage:5.1f}%",
            f"[{color}]{bar}[/{color}]"
        )

    return table


def create_cost_table(comparison: CostComparison) -> Table:
    """
    Create a formatted cost comparison table.

    Args:
        comparison: CostComparison object with cost analysis

    Returns:
        Rich Table object

    Example:
        >>> table = create_cost_table(comparison)
        >>> console.print(table)
    """
    table = Table(
        title="💰 Cost Comparison",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title_style="bold white"
    )

    table.add_column("Cost Type", style="cyan", justify="left")
    table.add_column("Current (RAG)", style="white", justify="right")
    table.add_column("After Fine-tuning", style="white", justify="right")
    table.add_column("Difference", style="", justify="right")

    # Per-query costs
    table.add_row(
        "Per Query",
        f"${comparison.rag_cost_per_query:.6f}",
        f"${comparison.finetuned_cost_per_query:.6f}",
        _format_difference(
            comparison.rag_cost_per_query - comparison.finetuned_cost_per_query
        )
    )

    # Monthly costs
    table.add_row(
        "Monthly",
        f"${comparison.monthly_rag_cost:,.2f}",
        f"${comparison.monthly_finetuned_cost:,.2f}",
        _format_difference(comparison.monthly_savings)
    )

    # Annual costs
    annual_rag = comparison.monthly_rag_cost * 12
    annual_finetuned = comparison.monthly_finetuned_cost * 12
    annual_savings = comparison.monthly_savings * 12

    table.add_row(
        "Annual",
        f"${annual_rag:,.2f}",
        f"${annual_finetuned:,.2f}",
        _format_difference(annual_savings)
    )

    # Training cost
    table.add_section()
    table.add_row(
        "Training (one-time)",
        "-",
        f"${comparison.training_cost:,.2f}",
        f"[yellow]one-time cost[/yellow]"
    )

    # Break-even
    if comparison.breakeven_months < float('inf') and comparison.monthly_savings > 0:
        breakeven_days = int(comparison.breakeven_months * 30)
        table.add_row(
            "Break-even",
            "-",
            f"{breakeven_days} days",
            f"[cyan]{comparison.breakeven_months:.1f} months[/cyan]"
        )

        # ROI
        annual_roi = (annual_savings / comparison.training_cost * 100) if comparison.training_cost > 0 else 0
        table.add_row(
            "ROI (annual)",
            "-",
            f"{annual_roi:,.0f}%",
            f"[green]return on investment[/green]"
        )

    return table


def create_cost_breakdown_table(comparison: CostComparison) -> Table:
    """
    Create a detailed cost breakdown table.

    Args:
        comparison: CostComparison object

    Returns:
        Rich Table object

    Example:
        >>> table = create_cost_breakdown_table(comparison)
        >>> console.print(table)
    """
    table = Table(
        title="Cost Breakdown (per query)",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title_style="bold white"
    )

    table.add_column("Component", style="cyan", justify="left")
    table.add_column("RAG System", style="white", justify="right")
    table.add_column("Fine-tuned", style="white", justify="right")

    # RAG components
    table.add_row(
        "Embedding",
        f"${comparison.rag_cost_per_query * 0.01:.6f}",  # Approximate
        "-"
    )

    table.add_row(
        "Vector Search",
        f"${comparison.rag_cost_per_query * 0.02:.6f}",  # Approximate
        "-"
    )

    table.add_row(
        "LLM (with context)",
        f"${comparison.rag_cost_per_query * 0.97:.6f}",  # Bulk of cost
        "-"
    )

    table.add_section()

    table.add_row(
        "LLM (no context)",
        "-",
        f"${comparison.finetuned_cost_per_query:.6f}"
    )

    table.add_section()

    table.add_row(
        "[bold]Total per query[/bold]",
        f"[bold]${comparison.rag_cost_per_query:.6f}[/bold]",
        f"[bold]${comparison.finetuned_cost_per_query:.6f}[/bold]"
    )

    return table


def create_top_queries_table(queries: list[tuple[str, float]], title: str = "Top Queries") -> Table:
    """
    Create a table showing top-performing queries.

    Args:
        queries: List of (query, score) tuples
        title: Table title

    Returns:
        Rich Table object

    Example:
        >>> table = create_top_queries_table(
        ...     [("How do I refund?", 0.98), ("Track shipment?", 0.96)],
        ...     "Best Performing Queries"
        ... )
    """
    table = Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title_style="bold white"
    )

    table.add_column("#", style="dim", justify="right", width=3)
    table.add_column("Query", style="white", justify="left")
    table.add_column("Score", style="green", justify="right")
    table.add_column("Quality", style="", justify="left")

    for i, (query, score) in enumerate(queries, 1):
        # Truncate long queries
        display_query = query[:70] + "..." if len(query) > 70 else query

        # Quality indicator
        if score >= 0.9:
            quality = "[green]excellent[/green]"
        elif score >= 0.8:
            quality = "[green]good[/green]"
        elif score >= 0.7:
            quality = "[yellow]fair[/yellow]"
        else:
            quality = "[red]poor[/red]"

        table.add_row(
            str(i),
            display_query,
            f"{score:.2f}",
            quality
        )

    return table


def _create_score_bar(score: float, width: int = 20) -> str:
    """
    Create a visual bar for a score (0.0-1.0).

    Args:
        score: Score value (0.0-1.0)
        width: Width of the bar in characters

    Returns:
        Colored bar string
    """
    filled = int(score * width)
    empty = width - filled

    if score >= 0.9:
        color = "green"
    elif score >= 0.8:
        color = "green"
    elif score >= 0.7:
        color = "yellow"
    else:
        color = "red"

    bar = f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"
    return bar


def _format_difference(value: float) -> str:
    """
    Format a cost difference with color coding.

    Args:
        value: Difference value (positive = savings)

    Returns:
        Formatted string with color
    """
    if value > 0:
        return f"[bold green]-${value:,.2f}[/bold green]"
    elif value < 0:
        return f"[bold red]+${abs(value):,.2f}[/bold red]"
    else:
        return "[dim]$0.00[/dim]"


def print_summary_panel(
    total_logs: int,
    filtered_logs: int,
    avg_score: float,
    monthly_savings: float
):
    """
    Print a summary panel with key metrics.

    Args:
        total_logs: Total number of logs analyzed
        filtered_logs: Number of high-quality logs
        avg_score: Average retrieval score
        monthly_savings: Monthly cost savings

    Example:
        >>> print_summary_panel(1234, 1089, 0.87, 206.0)
    """
    from rich.panel import Panel
    from rich.columns import Columns

    # Create metric panels
    metrics = []

    # Total logs
    metrics.append(
        Panel(
            f"[bold white]{total_logs:,}[/bold white]\n[dim]total logs[/dim]",
            border_style="blue",
            padding=(0, 2)
        )
    )

    # Quality rate
    quality_rate = (filtered_logs / total_logs * 100) if total_logs > 0 else 0
    color = "green" if quality_rate >= 70 else "yellow"
    metrics.append(
        Panel(
            f"[bold {color}]{quality_rate:.0f}%[/bold {color}]\n[dim]high quality[/dim]",
            border_style=color,
            padding=(0, 2)
        )
    )

    # Average score
    score_color = "green" if avg_score >= 0.8 else "yellow"
    metrics.append(
        Panel(
            f"[bold {score_color}]{avg_score:.2f}[/bold {score_color}]\n[dim]avg score[/dim]",
            border_style=score_color,
            padding=(0, 2)
        )
    )

    # Savings
    if monthly_savings > 0:
        metrics.append(
            Panel(
                f"[bold green]${monthly_savings:,.0f}[/bold green]\n[dim]monthly savings[/dim]",
                border_style="green",
                padding=(0, 2)
            )
        )

    # Display in columns
    console.print()
    console.print(Columns(metrics, equal=True, expand=True))
    console.print()
