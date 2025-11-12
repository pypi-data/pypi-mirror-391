"""
Progress indicators for Distillery CLI.

Provides beautiful progress bars and spinners using rich.
"""

from typing import Iterable, Optional, Callable, Any
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    MofNCompleteColumn
)
from rich.console import Console
from contextlib import contextmanager

console = Console()


def show_progress(
    iterable: Iterable,
    description: str,
    total: Optional[int] = None,
    transient: bool = False
) -> Iterable:
    """
    Show a progress bar while iterating.

    Args:
        iterable: The items to iterate over
        description: Description of what's being processed
        total: Total number of items (if known)
        transient: If True, progress bar disappears when done

    Example:
        >>> logs = list(range(1000))
        >>> for log in show_progress(logs, "Loading logs"):
        ...     process(log)
        Loading logs...  ━━━━━━━━━━━━━━ 854/1,000 (85%)  0:02 remaining
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=transient
    ) as progress:
        task = progress.add_task(description, total=total or len(list(iterable)))

        for item in iterable:
            yield item
            progress.advance(task)


def show_progress_with_callback(
    items: list,
    description: str,
    callback: Callable[[Any], None],
    transient: bool = False
) -> list:
    """
    Process items with a progress bar and callback function.

    Args:
        items: List of items to process
        description: Description of what's being processed
        callback: Function to call for each item
        transient: If True, progress bar disappears when done

    Returns:
        List of results from callback

    Example:
        >>> logs = load_logs()
        >>> filtered = show_progress_with_callback(
        ...     logs,
        ...     "Filtering logs",
        ...     lambda log: log if log.score > 0.8 else None
        ... )
    """
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=transient
    ) as progress:
        task = progress.add_task(description, total=len(items))

        for item in items:
            result = callback(item)
            if result is not None:
                results.append(result)
            progress.advance(task)

    return results


@contextmanager
def spinner(message: str, success_message: Optional[str] = None):
    """
    Show a spinner for indeterminate operations.

    Args:
        message: Message to show while spinning
        success_message: Message to show when done (optional)

    Example:
        >>> with spinner("Connecting to LangSmith..."):
        ...     client = connect_langsmith()
        ⠋ Connecting to LangSmith...

        >>> with spinner("Uploading to OpenAI...", "Upload complete!"):
        ...     upload_file()
        ⠋ Uploading to OpenAI...
        ✅ Upload complete!
    """
    from rich.spinner import Spinner
    from rich.live import Live
    from rich.text import Text

    spinner_obj = Spinner("dots", text=Text(message, style="cyan"))

    try:
        with Live(spinner_obj, console=console, transient=True):
            yield

        if success_message:
            from .console import success
            success(success_message)
    except Exception as e:
        from .console import error
        error(f"Failed: {str(e)}")
        raise


def multi_progress(tasks: dict[str, int]) -> Progress:
    """
    Create a multi-task progress tracker.

    Args:
        tasks: Dictionary of task names and their totals

    Returns:
        Progress object to use with context manager

    Example:
        >>> with multi_progress({"Loading": 100, "Processing": 50}) as progress:
        ...     task1 = progress.tasks["Loading"]
        ...     task2 = progress.tasks["Processing"]
        ...
        ...     for i in range(100):
        ...         progress.update(task1, advance=1)
        ...
        ...     for i in range(50):
        ...         progress.update(task2, advance=1)
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        console=console
    )

    # Add tasks
    for name, total in tasks.items():
        progress.add_task(name, total=total)

    return progress


def simple_progress(total: int, description: str = "Processing") -> Progress:
    """
    Create a simple progress bar for manual updates.

    Args:
        total: Total number of items
        description: Description text

    Returns:
        Tuple of (progress, task_id) for manual updates

    Example:
        >>> progress, task = simple_progress(100, "Loading logs")
        >>> with progress:
        ...     for i in range(100):
        ...         process_item(i)
        ...         progress.update(task, advance=1)
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    )

    task = progress.add_task(description, total=total)

    # Return both progress and task for convenience
    progress.task_id = task
    return progress


def download_progress(description: str = "Downloading") -> Progress:
    """
    Create a progress bar optimized for downloads.

    Shows bytes downloaded and speed.

    Args:
        description: Description text

    Returns:
        Progress object

    Example:
        >>> progress = download_progress("Downloading model")
        >>> task = progress.add_task(description, total=file_size)
        >>> with progress:
        ...     for chunk in download_chunks():
        ...         progress.update(task, advance=len(chunk))
    """
    from rich.progress import DownloadColumn, TransferSpeedColumn

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        DownloadColumn(),
        TransferSpeedColumn(),
        console=console
    )

    return progress
