"""
Console output helpers for Distillery CLI.

Provides consistent, beautiful output using rich.
"""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

# Global console instance
console = Console()


def success(message: str, detail: Optional[str] = None):
    """
    Print a success message.

    Args:
        message: Main success message
        detail: Optional detail text

    Example:
        >>> success("Training completed!", "Model: ft:gpt-4o-mini:v1")
    """
    text = Text()
    text.append("✅ ", style="bold green")
    text.append(message, style="green")

    if detail:
        text.append(f"\n   {detail}", style="dim")

    console.print(text)


def error(message: str, suggestions: Optional[list] = None, help_url: Optional[str] = None):
    """
    Print an error message with helpful suggestions.

    Args:
        message: Error message
        suggestions: List of suggestions to fix the error
        help_url: Optional help documentation URL

    Example:
        >>> error(
        ...     "Could not find log files",
        ...     suggestions=[
        ...         "Check the path is correct",
        ...         "Ensure files have .jsonl extension"
        ...     ],
        ...     help_url="https://docs.distillery.ai/troubleshooting"
        ... )
    """
    text = Text()
    text.append("❌ ", style="bold red")
    text.append(message, style="red bold")
    console.print(text)

    if suggestions:
        console.print()
        for suggestion in suggestions:
            console.print(f"  • {suggestion}", style="yellow")

    if help_url:
        console.print()
        console.print(f"Need help? {help_url}", style="dim blue")


def warning(message: str, detail: Optional[str] = None):
    """
    Print a warning message.

    Args:
        message: Warning message
        detail: Optional detail text

    Example:
        >>> warning("Low quality data detected", "Only 60% of logs are usable")
    """
    text = Text()
    text.append("⚠️  ", style="bold yellow")
    text.append(message, style="yellow")

    if detail:
        text.append(f"\n   {detail}", style="dim")

    console.print(text)


def info(message: str, icon: str = "ℹ️"):
    """
    Print an info message.

    Args:
        message: Info message
        icon: Optional icon (default: ℹ️)

    Example:
        >>> info("Loading logs from LangSmith...")
    """
    text = Text()
    text.append(f"{icon} ", style="bold cyan")
    text.append(message, style="cyan")
    console.print(text)


def section(title: str):
    """
    Print a section header.

    Args:
        title: Section title

    Example:
        >>> section("Quality Assessment")
    """
    console.print()
    console.print(title, style="bold white")


def welcome():
    """
    Print welcome message when user runs 'distillery' with no args.
    """
    welcome_text = """
# Distillery 🧪

**Convert RAG logs into fine-tuning datasets**

## Commands

- `analyze`   - Analyze your RAG logs and see if fine-tuning makes sense
- `generate`  - Generate training dataset from your logs
- `compare`   - Compare RAG vs fine-tuning costs in detail
- `train`     - Upload and start fine-tuning

## Examples

```bash
# Quick start
distillery analyze logs/*.jsonl
distillery generate logs/*.jsonl
distillery train training_data.jsonl

# From LangSmith
distillery analyze --source langsmith --project my-rag-app

# With custom filters
distillery generate logs/*.jsonl --min-score 0.90
```

## Get Started

Run `distillery analyze logs/*.jsonl` to see if fine-tuning will save you money.

Learn more: https://docs.distillery.ai
"""
    console.print(Markdown(welcome_text))


def show_cost_savings(
    monthly_rag_cost: float,
    monthly_finetuned_cost: float,
    monthly_savings: float,
    training_cost: float,
    breakeven_months: float
):
    """
    Show cost savings in a beautiful format.

    Args:
        monthly_rag_cost: Monthly RAG cost
        monthly_finetuned_cost: Monthly fine-tuned cost
        monthly_savings: Monthly savings
        training_cost: One-time training cost
        breakeven_months: Months to break even
    """
    section("💰 Cost Analysis")

    # Create formatted strings
    console.print(f"  Current (RAG):     ${monthly_rag_cost:,.2f}/month", style="white")
    console.print(f"  After fine-tuning: ${monthly_finetuned_cost:,.2f}/month", style="white")

    if monthly_savings > 0:
        console.print(f"  [bold green]Monthly savings:   ${monthly_savings:,.2f}[/bold green]")
        console.print(f"  [dim]Annual savings:    ${monthly_savings * 12:,.2f}[/dim]")
        console.print(f"  [dim]Training cost:     ${training_cost:,.2f} (one-time)[/dim]")

        if breakeven_months < float('inf'):
            breakeven_days = int(breakeven_months * 30)
            console.print(f"  [bold cyan]Break-even:        {breakeven_days} days[/bold cyan]")

            # Calculate ROI
            annual_return = (monthly_savings * 12 / training_cost * 100) if training_cost > 0 else 0
            console.print(f"  [dim]ROI:               {annual_return:,.0f}% annual return[/dim]")
    else:
        console.print(f"  [yellow]Note: Fine-tuning not cost-effective at this scale[/yellow]")


def show_recommendation(
    should_finetune: bool,
    quality_pct: float,
    monthly_savings: float,
    breakeven_days: int
):
    """
    Show recommendation with reasoning.

    Args:
        should_finetune: Whether fine-tuning is recommended
        quality_pct: Percentage of high-quality data
        monthly_savings: Monthly savings amount
        breakeven_days: Days to break even
    """
    console.print()

    if should_finetune:
        panel_content = Text()
        panel_content.append("Fine-tuning is highly recommended\n\n", style="bold green")
        panel_content.append(f"• {quality_pct:.0f}% of your data is high quality\n")
        panel_content.append(f"• You'll save ${monthly_savings:,.0f} every month\n")
        panel_content.append(f"• Break-even in just {breakeven_days} days\n")
        panel_content.append("• Responses will be 3-5x faster")

        console.print(Panel(
            panel_content,
            title="✅ Recommendation",
            border_style="green"
        ))
    else:
        panel_content = Text()
        panel_content.append("Fine-tuning not recommended yet\n\n", style="bold yellow")

        if quality_pct < 70:
            panel_content.append(f"• Only {quality_pct:.0f}% of data is high quality (need >70%)\n")
            panel_content.append("• Consider improving your RAG system first\n")
        else:
            panel_content.append("• Your dataset is too small for cost savings\n")
            panel_content.append("• Wait until you have more production data\n")

        panel_content.append("\nRun with --verbose for detailed analysis")

        console.print(Panel(
            panel_content,
            title="⚠️  Recommendation",
            border_style="yellow"
        ))


def show_next_steps(steps: list[str]):
    """
    Show next steps to guide the user.

    Args:
        steps: List of steps (with command examples)

    Example:
        >>> show_next_steps([
        ...     "Generate training data: distillery generate logs/*.jsonl",
        ...     "Review the output: head training_data.jsonl | jq"
        ... ])
    """
    console.print()
    section("Next Steps")

    for i, step in enumerate(steps, 1):
        if ":" in step:
            action, command = step.split(":", 1)
            console.print(f"  {i}. {action.strip()}:")
            console.print(f"     [cyan]{command.strip()}[/cyan]")
        else:
            console.print(f"  {i}. {step}")
