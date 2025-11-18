"""Live display with progress bar and scrolling log window."""

import time
from collections import deque
from rich.console import Console, Group
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text


class LiveProgressDisplay:
    """
    Live display with single progress bar and scrolling log window.

    Shows:
    - Top: One progress bar for current stage
    - Bottom: Scrolling log window (max 10 lines) showing recent activity
    """

    def __init__(self, console: Console = None, max_log_lines: int = 10):
        """
        Initialize live progress display.

        Args:
            console: Rich Console instance
            max_log_lines: Maximum number of log lines to show (default: 10)
        """
        self.console = console or Console()
        self.max_log_lines = max_log_lines
        self.log_buffer = deque(maxlen=max_log_lines)

        # Create progress bar
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        )

        # Current task
        self.current_task = None
        self.live = None

    def __enter__(self):
        """Start live display."""
        self.live = Live(
            self._render(),
            console=self.console,
            refresh_per_second=4,
            vertical_overflow="visible",
        )
        self.live.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop live display."""
        if self.live:
            self.live.__exit__(exc_type, exc_val, exc_tb)

    def _render(self):
        """Render progress bar + log lines (no frame)."""
        # Build log lines (no panel, just plain text)
        log_lines = []
        for line in self.log_buffer:
            log_lines.append(line)

        # Combine progress + log lines
        if log_lines:
            return Group(
                self.progress,
                "",  # Empty line for spacing
                *log_lines,  # Unpack log lines directly
            )
        else:
            return self.progress

    def update_display(self):
        """Update the live display."""
        if self.live:
            self.live.update(self._render())

    def start_stage(self, description: str, total: int = None):
        """
        Start a new stage with progress bar.

        Args:
            description: Stage description (e.g., "Fetching content")
            total: Total items (None for indeterminate)

        Returns:
            Task ID
        """
        if self.current_task is not None:
            # Complete previous task
            self.progress.update(self.current_task, visible=False)

        self.current_task = self.progress.add_task(description, total=total)
        self.update_display()
        return self.current_task

    def update_progress(self, task_id: int = None, advance: int = None, completed: int = None, description: str = None):
        """
        Update progress bar.

        Args:
            task_id: Task ID (uses current task if None)
            advance: Increment progress by N
            completed: Set progress to N
            description: Update description
        """
        if task_id is None:
            task_id = self.current_task

        if task_id is not None:
            kwargs = {}
            if advance is not None:
                kwargs["advance"] = advance
            if completed is not None:
                kwargs["completed"] = completed
            if description is not None:
                kwargs["description"] = description

            self.progress.update(task_id, **kwargs)
            self.update_display()

    def complete_stage(self, task_id: int = None):
        """
        Complete current stage.

        Args:
            task_id: Task ID (uses current task if None)
        """
        if task_id is None:
            task_id = self.current_task

        if task_id is not None:
            self.progress.update(task_id, completed=self.progress.tasks[task_id].total or 100)
            self.update_display()

    def log(self, message: str, style: str = ""):
        """
        Add a log message to scrolling window.

        Args:
            message: Log message
            style: Rich style (e.g., "green", "red", "dim")
        """
        # Escape square brackets in message to prevent Rich from interpreting them as markup
        # Replace [ with \[ and ] with \] but only in the message content, not in style tags
        from rich.markup import escape
        escaped_message = escape(message)

        if style:
            formatted = f"[{style}]{escaped_message}[/{style}]"
        else:
            formatted = escaped_message

        self.log_buffer.append(formatted)
        self.update_display()

    def log_success(self, doc_id: str, title: str, elapsed: float = None, timing_breakdown: dict = None, operation: str = None, counter: tuple[int, int] = None):
        """
        Log successful operation.

        Args:
            doc_id: Document ID (short form)
            title: Document title
            elapsed: Total elapsed time
            timing_breakdown: Dict of step timings (e.g., {"load": 0.5, "llm": 2.0, "db": 0.1})
            operation: Operation type (e.g., "Fetched", "Indexed") - optional
            counter: Tuple of (current, total) for progress counter (e.g., (1, 29))
        """
        # Ensure doc_id is not empty
        if not doc_id or not doc_id.strip():
            short_id = "????????"
        else:
            short_id = doc_id[:8] if len(doc_id) > 8 else doc_id

        # Extra safety: ensure short_id is never empty (would break Rich markup)
        if not short_id or not short_id.strip():
            short_id = "????????"

        short_title = title[:50] + "..." if len(title) > 50 else title

        # Add counter prefix if provided
        counter_prefix = f"{counter[0]}/{counter[1]} " if counter else ""

        # Add operation prefix if provided
        prefix = f"{operation}: " if operation else ""

        if timing_breakdown:
            timing_str = ", ".join([f"{k}={v:.1f}s" for k, v in timing_breakdown.items()])
            msg = f"{counter_prefix}✓ {prefix}[{short_id}] {short_title} ({elapsed:.1f}s: {timing_str})"
        elif elapsed:
            msg = f"{counter_prefix}✓ {prefix}[{short_id}] {short_title} ({elapsed:.1f}s)"
        else:
            msg = f"{counter_prefix}✓ {prefix}[{short_id}] {short_title}"

        self.log(msg, style="dim green")

    def log_skip(self, doc_id: str, title: str, reason: str = "content unchanged", operation: str = None, counter: tuple[int, int] = None):
        """
        Log skipped operation.

        Args:
            doc_id: Document ID (short form)
            title: Document title
            reason: Skip reason
            operation: Operation type (e.g., "Skipped") - optional
            counter: Tuple of (current, total) for progress counter (e.g., (1, 29))
        """
        # Ensure doc_id is not empty
        if not doc_id or not doc_id.strip():
            short_id = "????????"
        else:
            short_id = doc_id[:8] if len(doc_id) > 8 else doc_id

        # Extra safety: ensure short_id is never empty (would break Rich markup)
        if not short_id or not short_id.strip():
            short_id = "????????"

        short_title = title[:50] + "..." if len(title) > 50 else title
        counter_prefix = f"{counter[0]}/{counter[1]} " if counter else ""
        prefix = f"{operation}: " if operation else ""
        msg = f"{counter_prefix}○ {prefix}[{short_id}] {short_title} ({reason})"
        self.log(msg, style="dim yellow")

    def log_error(self, doc_id: str, error: str, operation: str = None, counter: tuple[int, int] = None):
        """
        Log error.

        Args:
            doc_id: Document ID (short form)
            error: Error message
            operation: Operation type (e.g., "Fetch failed", "Index failed") - optional
            counter: Tuple of (current, total) for progress counter (e.g., (1, 29))
        """
        # Ensure doc_id is not empty
        if not doc_id or not doc_id.strip():
            short_id = "????????"
        else:
            short_id = doc_id[:8] if len(doc_id) > 8 else doc_id

        # Extra safety: ensure short_id is never empty (would break Rich markup)
        if not short_id or not short_id.strip():
            short_id = "????????"

        counter_prefix = f"{counter[0]}/{counter[1]} " if counter else ""
        prefix = f"{operation}: " if operation else ""
        msg = f"{counter_prefix}✗ {prefix}[{short_id}] {error}"
        self.log(msg, style="dim red")

    def log_info(self, message: str):
        """
        Log informational message.

        Args:
            message: Info message
        """
        self.log(f"ℹ {message}", style="dim cyan")


def create_fetch_progress_callback(display: LiveProgressDisplay, total_docs: int):
    """
    Create progress callback for fetch + index operations.

    Args:
        display: LiveProgressDisplay instance
        total_docs: Total documents to process

    Returns:
        Callback function
    """
    indexed_count = 0
    doc_start_times = {}
    doc_step_times = {}
    doc_resolved_ids = {}  # Track mapping from input ID to resolved UUID

    def callback(doc_id: str, title: str, status: str, activity: str = None, skip_reason: str = None):
        nonlocal indexed_count

        if activity:
            # Activity update - track timing
            if doc_id not in doc_start_times:
                doc_start_times[doc_id] = time.time()
                doc_step_times[doc_id] = {}

            doc_step_times[doc_id][activity] = time.time()

            # Update progress bar description
            display.update_progress(description=f"Indexing ({indexed_count}/{total_docs}): {activity}")
        else:
            # Completion update
            indexed_count += 1

            # Use doc_id and title directly (no prefix extraction needed)
            display_doc_id = doc_id
            display_title = title

            # Calculate timing
            if doc_id in doc_start_times:
                total_time = time.time() - doc_start_times[doc_id]

                # Calculate step timings
                step_times = doc_step_times.get(doc_id, {})
                steps = list(step_times.keys())

                timing_breakdown = {}
                for i, step in enumerate(steps):
                    step_start = step_times[step]
                    if i < len(steps) - 1:
                        step_end = step_times[steps[i + 1]]
                    else:
                        step_end = time.time()

                    duration = step_end - step_start

                    # Shorten step names
                    step_short = step.replace("Loading existing entities...", "load")
                    step_short = step_short.replace("Calling LLM to extract metadata...", "llm")
                    step_short = step_short.replace("Updating database...", "db")

                    timing_breakdown[step_short] = duration

                # Log based on status (use display_doc_id for showing, display_title for text)
                counter = (indexed_count, total_docs)
                if status == "success":
                    display.log_success(display_doc_id, display_title, total_time, timing_breakdown, operation="Indexed", counter=counter)
                elif status == "skipped":
                    display.log_skip(display_doc_id, display_title, skip_reason or "content unchanged", operation="Skipped", counter=counter)
                elif status == "error":
                    display.log_error(display_doc_id, display_title, operation="Index failed", counter=counter)

                # Cleanup
                doc_start_times.pop(doc_id, None)
                doc_step_times.pop(doc_id, None)
            else:
                # No timing info, just log
                counter = (indexed_count, total_docs)
                if status == "success":
                    display.log_success(display_doc_id, display_title, operation="Indexed", counter=counter)
                elif status == "skipped":
                    display.log_skip(display_doc_id, display_title, skip_reason or "content unchanged", operation="Skipped", counter=counter)
                elif status == "error":
                    display.log_error(display_doc_id, display_title, operation="Index failed", counter=counter)

            # Update progress bar
            display.update_progress(completed=indexed_count)

    return callback
