"""Shared indexing utilities for content commands."""

import time
from rich.console import Console

from kurt.commands.content._live_display import LiveProgressDisplay, create_fetch_progress_callback


def index_single_document_with_progress(doc, console: Console, force: bool = False):
    """
    Index a single document with live display and activity tracking.

    Args:
        doc: Document object to index
        console: Rich Console instance
        force: Force re-indexing even if already indexed

    Returns:
        dict with keys:
            - success: bool
            - result: dict (if successful)
            - error: str (if failed)
            - skipped: bool
    """
    from kurt.content.indexing import extract_document_metadata

    doc_id = str(doc.id)

    with LiveProgressDisplay(console, max_log_lines=10) as display:
        display.start_stage("Indexing document", total=None)

        try:
            # Activity callback for single document
            def activity_callback(activity: str):
                display.log_info(activity)

            # Extract and persist metadata + entities with activity tracking
            start_time = time.time()

            result = extract_document_metadata(
                doc_id, force=force, activity_callback=activity_callback
            )

            elapsed = time.time() - start_time

            if result.get("skipped", False):
                skip_reason = result.get("skip_reason", "content unchanged")
                title = result.get("title", "Untitled")
                display.log_skip(doc_id, title, skip_reason)
                display.complete_stage()
                return {"success": True, "result": result, "skipped": True}
            else:
                display.log_success(doc_id, result['title'], elapsed)
                display.complete_stage()
                return {"success": True, "result": result, "skipped": False}

        except Exception as e:
            display.log_error(doc_id, str(e))
            display.complete_stage()
            return {"success": False, "error": str(e), "skipped": False}


def index_multiple_documents_with_progress(documents, console: Console, force: bool = False):
    """
    Index multiple documents with live display and activity tracking.

    Args:
        documents: List of Document objects to index
        console: Rich Console instance
        force: Force re-indexing even if already indexed

    Returns:
        dict with keys from batch_extract_document_metadata:
            - results: list of result dicts
            - errors: list of error dicts
            - succeeded: int
            - failed: int
            - skipped: int
            - elapsed_time: float (total seconds)
    """
    import asyncio
    import time
    from kurt.content.indexing import batch_extract_document_metadata
    from kurt.config import load_config

    # Extract document IDs
    document_ids = [str(doc.id) for doc in documents]

    # Get max concurrent from config
    config = load_config()
    max_concurrent = config.MAX_CONCURRENT_INDEXING

    # Track overall timing
    start_time = time.time()

    with LiveProgressDisplay(console, max_log_lines=10) as display:
        # Start indexing stage
        display.start_stage("Indexing documents", total=len(document_ids))

        # Create progress callback with activity updates and logging
        update_progress = create_fetch_progress_callback(display, len(document_ids))

        # Run async batch extraction with progress callback
        batch_result = asyncio.run(
            batch_extract_document_metadata(
                document_ids, max_concurrent=max_concurrent, force=force, progress_callback=update_progress
            )
        )

        display.complete_stage()

    # Add elapsed time to result
    batch_result["elapsed_time"] = time.time() - start_time

    return batch_result


def display_kg_finalization_summary(kg_result, console: Console):
    """
    Display knowledge graph finalization summary.

    Args:
        kg_result: Result dict from finalize_knowledge_graph_from_index_results
        console: Rich Console instance
    """
    console.print("\n[bold]Finalizing knowledge graph...[/bold]")

    if "error" in kg_result:
        console.print(f"  [red]✗[/red] KG finalization failed: {kg_result['error']}")
    else:
        console.print(f"  [green]✓[/green] Created {kg_result['entities_created']} entities")
        console.print(f"  [green]✓[/green] Linked {kg_result['entities_linked']} entities")
        if kg_result.get("relationships_created", 0) > 0:
            console.print(f"  [green]✓[/green] Created {kg_result['relationships_created']} relationships")
