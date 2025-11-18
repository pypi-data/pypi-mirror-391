"""Shared progress bar utilities for content commands."""

import time


def create_indexing_progress_callback(progress, task_id, total_docs: int, show_timing: bool = True):
    """
    Create a progress callback for indexing operations.

    This callback displays real-time activity updates during document indexing,
    showing what's happening at each step (loading entities, calling LLM, updating DB).

    Args:
        progress: Rich Progress instance
        task_id: Task ID from progress.add_task()
        total_docs: Total number of documents being indexed
        show_timing: If True, print timestamped completion logs with step breakdown

    Returns:
        Callable progress callback function(doc_id, title, status, activity=None, skip_reason=None)

    Example:
        with Progress(...) as progress:
            task = progress.add_task("Indexing...", total=len(docs))
            callback = create_indexing_progress_callback(progress, task, len(docs))
            await batch_extract_document_metadata(docs, progress_callback=callback)
    """
    indexed_count = 0
    current_activities = {}
    doc_start_times = {}  # Track when each document started
    doc_step_times = {}  # Track timing for each step

    def update_progress(doc_id: str, title: str, status: str, activity: str = None, skip_reason: str = None):
        nonlocal indexed_count

        if activity:
            # Activity update (interim progress during processing)
            current_activities[doc_id] = activity

            # Track start time for this doc if not already tracked
            if doc_id not in doc_start_times:
                doc_start_times[doc_id] = time.time()
                doc_step_times[doc_id] = {}

            # Record when this step started
            now = time.time()
            doc_step_times[doc_id][activity] = now

            desc = f"Indexing ({indexed_count}/{total_docs}): {activity}"
            progress.update(task_id, description=desc)
        else:
            # Completion update (document finished)
            indexed_count += 1
            current_activities.pop(doc_id, None)

            # Print timestamped completion log using progress.console to avoid overwrites
            if show_timing and doc_id in doc_start_times:
                total_time = time.time() - doc_start_times[doc_id]
                short_id = doc_id[:8]
                short_title = title[:40] + "..." if len(title) > 40 else title

                if status == "success":
                    # Calculate step timings
                    step_times = doc_step_times.get(doc_id, {})
                    steps = list(step_times.keys())

                    # Build timing breakdown
                    timing_parts = []
                    for i, step in enumerate(steps):
                        step_start = step_times[step]
                        # Duration is from this step to next step (or to now for last step)
                        if i < len(steps) - 1:
                            step_end = step_times[steps[i + 1]]
                        else:
                            step_end = time.time()

                        duration = step_end - step_start

                        # Shorten step names for display
                        step_short = step.replace("Loading existing entities...", "load")
                        step_short = step_short.replace("Calling LLM to extract metadata...", "llm")
                        step_short = step_short.replace("Updating database...", "db")

                        timing_parts.append(f"{step_short}={duration:.2f}s")

                    timing_str = ", ".join(timing_parts) if timing_parts else ""

                    progress.console.print(
                        f"  [dim]✓ [{short_id}] {short_title} ({total_time:.2f}s: {timing_str})[/dim]"
                    )
                elif status == "skipped":
                    reason = skip_reason or "content unchanged"
                    progress.console.print(f"  [dim]○ [{short_id}] {short_title} - Skipped ({reason})[/dim]")
                elif status == "error":
                    progress.console.print(f"  [dim]✗ [{short_id}] Failed: {title}[/dim]")

                # Clean up tracking
                doc_start_times.pop(doc_id, None)
                doc_step_times.pop(doc_id, None)

            if current_activities:
                # Show most recent ongoing activity
                latest_activity = list(current_activities.values())[-1]
                desc = f"Indexing ({indexed_count}/{total_docs}): {latest_activity}"
            else:
                # No ongoing activities, show clean progress
                desc = f"Indexing ({indexed_count}/{total_docs})"

            progress.update(task_id, description=desc, completed=indexed_count)

    return update_progress
