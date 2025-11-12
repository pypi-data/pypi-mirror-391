"""
UI components for Distillery CLI.

Beautiful, consistent output using rich library.
"""

from .console import (
    console,
    success,
    error,
    warning,
    info,
    section,
    welcome,
    show_cost_savings,
    show_recommendation,
    show_next_steps
)
from .progress import (
    show_progress,
    show_progress_with_callback,
    spinner,
    simple_progress,
    multi_progress,
    download_progress
)
from .tables import (
    create_stats_table,
    create_quality_distribution_table,
    create_cost_table,
    create_cost_breakdown_table,
    create_top_queries_table,
    print_summary_panel
)

__all__ = [
    # Console
    "console",
    "success",
    "error",
    "warning",
    "info",
    "section",
    "welcome",
    "show_cost_savings",
    "show_recommendation",
    "show_next_steps",
    # Progress
    "show_progress",
    "show_progress_with_callback",
    "spinner",
    "simple_progress",
    "multi_progress",
    "download_progress",
    # Tables
    "create_stats_table",
    "create_quality_distribution_table",
    "create_cost_table",
    "create_cost_breakdown_table",
    "create_top_queries_table",
    "print_summary_panel",
]
