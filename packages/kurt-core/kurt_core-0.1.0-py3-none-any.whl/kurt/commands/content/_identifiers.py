"""Common identifier resolution logic for content commands.

This module provides utilities to resolve identifiers (ID/URL/file path) to document IDs,
with support for partial UUIDs (minimum 8 characters).
"""

import os
from typing import Optional


def resolve_identifier_to_doc_id(identifier: str) -> str:
    """
    Resolve an identifier (ID, URL, or file path) to a document ID.

    Supports:
    - Full UUIDs: "550e8400-e29b-41d4-a716-446655440000"
    - Partial UUIDs: "550e8400" (minimum 8 characters)
    - URLs: "https://example.com/article"
    - File paths: "./docs/article.md"

    Args:
        identifier: Document ID, URL, or file path

    Returns:
        Document ID as string (full UUID)

    Raises:
        ValueError: If identifier cannot be resolved or is ambiguous

    Example:
        doc_id = resolve_identifier_to_doc_id("550e8400")
        doc_id = resolve_identifier_to_doc_id("https://example.com/article")
        doc_id = resolve_identifier_to_doc_id("./docs/article.md")
    """
    from kurt.content.document import get_document, list_documents

    # Check if it's a URL
    if identifier.startswith(("http://", "https://")):
        # Look up document by URL
        matching_docs = [d for d in list_documents() if d.source_url == identifier]
        if not matching_docs:
            raise ValueError(f"Document not found: {identifier}")
        return str(matching_docs[0].id)

    # Check if it's a file path
    elif os.path.exists(identifier) or identifier.startswith(("./", "../", "/")) or "/" in identifier:
        # Look up document by content_path
        # Try both absolute and relative path matching
        abs_path = os.path.abspath(identifier)

        # Get all documents
        all_docs = list_documents()

        # Try multiple matching strategies
        matching_docs = []

        # Strategy 1: Exact match on content_path
        for d in all_docs:
            if d.content_path == identifier:
                matching_docs.append(d)

        # Strategy 2: Absolute path match
        if not matching_docs:
            for d in all_docs:
                if d.content_path and os.path.abspath(d.content_path) == abs_path:
                    matching_docs.append(d)

        # Strategy 3: Relative path from sources/ directory (common case)
        if not matching_docs and identifier.startswith("sources/"):
            rel_path = identifier[8:]  # Remove "sources/" prefix
            for d in all_docs:
                if d.content_path and d.content_path == rel_path:
                    matching_docs.append(d)

        # Strategy 4: Suffix match (last resort)
        if not matching_docs:
            for d in all_docs:
                if d.content_path and d.content_path.endswith(identifier):
                    matching_docs.append(d)

        if not matching_docs:
            raise ValueError(f"Document not found for file: {identifier}\nTip: Use 'kurt content list' to see available documents")

        if len(matching_docs) > 1:
            raise ValueError(
                f"Ambiguous file path: {identifier} matches {len(matching_docs)} documents. "
                f"Use document ID instead."
            )

        return str(matching_docs[0].id)

    # Assume it's a document ID (full or partial)
    else:
        # get_document already supports partial UUIDs
        doc = get_document(identifier)
        return str(doc.id)


def resolve_ids_to_uuids(ids_str: str) -> list[str]:
    """
    Resolve comma-separated identifiers to full UUIDs.

    Each identifier can be:
    - Full UUID
    - Partial UUID (minimum 8 characters)
    - URL (resolves to document with that URL)
    - File path (resolves to document with that content_path)

    Args:
        ids_str: Comma-separated list of identifiers

    Returns:
        List of full UUIDs as strings

    Raises:
        ValueError: If any identifier cannot be resolved

    Example:
        uuids = resolve_ids_to_uuids("550e8400,https://example.com/article,docs/file.md")
    """
    uuids = []
    errors = []

    for id_str in ids_str.split(","):
        id_str = id_str.strip()
        if not id_str:
            continue

        try:
            doc_id = resolve_identifier_to_doc_id(id_str)
            uuids.append(doc_id)
        except ValueError as e:
            errors.append(f"{id_str}: {e}")

    if errors:
        raise ValueError(f"Failed to resolve identifiers:\n" + "\n".join(errors))

    return uuids
