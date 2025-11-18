"""Common filter resolution logic for content commands.

This module provides a unified way to resolve and merge document filters,
especially handling the positional IDENTIFIER argument merging into --ids filter.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DocumentFilters:
    """Resolved document filters for querying.

    Attributes:
        ids: Comma-separated document IDs (supports partial UUIDs, URLs, file paths)
        include_pattern: Glob pattern matching source_url or content_path
        in_cluster: Cluster name filter
        with_status: Ingestion status filter (NOT_FETCHED, FETCHED, ERROR)
        with_content_type: Content type filter (tutorial, guide, blog, etc.)
        limit: Maximum number of documents to process/display
        exclude_pattern: Glob pattern for exclusion (used in fetch)
    """

    ids: Optional[str] = None
    include_pattern: Optional[str] = None
    in_cluster: Optional[str] = None
    with_status: Optional[str] = None
    with_content_type: Optional[str] = None
    limit: Optional[int] = None
    exclude_pattern: Optional[str] = None


def resolve_filters(
    identifier: Optional[str] = None,
    ids: Optional[str] = None,
    include_pattern: Optional[str] = None,
    in_cluster: Optional[str] = None,
    with_status: Optional[str] = None,
    with_content_type: Optional[str] = None,
    limit: Optional[int] = None,
    exclude_pattern: Optional[str] = None,
) -> DocumentFilters:
    """
    Resolve and merge filters, especially handling positional IDENTIFIER.

    The positional IDENTIFIER argument (if provided) is resolved to a document ID
    and merged into the ids filter. This provides a clean API where:
    - `kurt index DOC_ID` is shorthand for `kurt index --ids DOC_ID`
    - `kurt index DOC_ID --ids "ID1,ID2"` becomes `--ids "DOC_ID,ID1,ID2"`

    Args:
        identifier: Positional identifier (doc ID, URL, or file path)
        ids: Comma-separated document IDs
        include_pattern: Glob pattern for inclusion
        in_cluster: Cluster name filter
        with_status: Ingestion status filter
        with_content_type: Content type filter
        limit: Maximum number of documents
        exclude_pattern: Glob pattern for exclusion

    Returns:
        DocumentFilters instance with resolved and merged filters

    Example:
        # Simple case
        filters = resolve_filters(identifier="44ea066e")
        # filters.ids == "44ea066e-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        # Merging case
        filters = resolve_filters(
            identifier="44ea066e",
            ids="550e8400,a73af781",
            include_pattern="*/docs/*"
        )
        # filters.ids == "44ea066e-xxxx-xxxx-xxxx-xxxxxxxxxxxx,550e8400,a73af781"
        # filters.include_pattern == "*/docs/*"
    """
    from kurt.commands.content._identifiers import resolve_identifier_to_doc_id

    # If identifier provided, resolve and merge into ids
    resolved_ids = ids
    if identifier:
        try:
            doc_id = resolve_identifier_to_doc_id(identifier)
            if resolved_ids:
                # Merge: identifier comes first
                resolved_ids = f"{doc_id},{resolved_ids}"
            else:
                resolved_ids = doc_id
        except ValueError as e:
            # Let the caller handle the error
            raise ValueError(f"Failed to resolve identifier '{identifier}': {e}")

    return DocumentFilters(
        ids=resolved_ids,
        include_pattern=include_pattern,
        in_cluster=in_cluster,
        with_status=with_status,
        with_content_type=with_content_type,
        limit=limit,
        exclude_pattern=exclude_pattern,
    )
