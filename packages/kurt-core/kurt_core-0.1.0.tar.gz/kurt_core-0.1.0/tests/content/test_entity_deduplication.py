"""Test entity deduplication during re-indexing."""

import pytest
from sqlalchemy import text
from sqlmodel import select

from kurt.db.database import get_session
from kurt.db.models import Entity, EntityRelationship, DocumentEntity
from kurt.content.indexing import extract_document_metadata, finalize_knowledge_graph_from_index_results


def clear_all_entities_and_relationships():
    """Clear all entities, relationships, and document-entity links from database."""
    session = get_session()

    # Delete in order to respect foreign key constraints
    session.exec(text("DELETE FROM document_entities"))
    session.exec(text("DELETE FROM entity_relationships"))
    session.exec(text("DELETE FROM entities"))

    session.commit()

    # Verify deletion
    entities_count = len(session.exec(select(Entity)).all())
    relationships_count = len(session.exec(select(EntityRelationship)).all())
    doc_entities_count = len(session.exec(select(DocumentEntity)).all())

    assert entities_count == 0, f"Expected 0 entities, found {entities_count}"
    assert relationships_count == 0, f"Expected 0 relationships, found {relationships_count}"
    assert doc_entities_count == 0, f"Expected 0 document-entity links, found {doc_entities_count}"

    print(f"✓ Cleared all entities, relationships, and document-entity links")


def get_entity_counts():
    """Get counts of entities, relationships, and document-entity links."""
    session = get_session()

    entities = session.exec(select(Entity)).all()
    relationships = session.exec(select(EntityRelationship)).all()
    doc_entities = session.exec(select(DocumentEntity)).all()

    return {
        "entities": len(entities),
        "relationships": len(relationships),
        "doc_entities": len(doc_entities),
        "entity_names": [e.name for e in entities],
    }


def check_for_duplicate_entities():
    """Check for duplicate entities by name and type."""
    session = get_session()

    # Query for duplicate entities (same name and type)
    duplicates_query = text("""
        SELECT name, type, COUNT(*) as count
        FROM entities
        GROUP BY name, type
        HAVING COUNT(*) > 1
    """)

    duplicates = session.exec(duplicates_query).all()

    if duplicates:
        print("\n❌ Found duplicate entities:")
        for name, entity_type, count in duplicates:
            print(f"  - {name} ({entity_type}): {count} instances")
        return False, duplicates

    print("✓ No duplicate entities found")
    return True, []


@pytest.mark.integration
def test_reindex_no_duplicates():
    """Test that re-indexing documents multiple times doesn't create duplicate entities."""

    # Step 1: Clear all entities and relationships
    print("\n=== Step 1: Clearing all entities and relationships ===")
    clear_all_entities_and_relationships()

    # Step 2: Get test documents (use first 3 documents)
    from kurt.content.document import list_documents_for_indexing

    documents = list_documents_for_indexing(all_flag=True)
    test_docs = documents[:3]  # Use 3 documents

    if len(test_docs) < 3:
        pytest.skip("Need at least 3 documents in database for this test")

    doc_ids = [str(doc.id) for doc in test_docs]
    print(f"\n=== Using {len(doc_ids)} test documents ===")
    for i, doc in enumerate(test_docs, 1):
        doc_name = doc.title or doc.source_url or "Untitled"
        print(f"  {i}. {doc_name} ({doc.id})")

    # Step 3: Index documents for the first time
    print("\n=== Step 2: First indexing pass ===")

    index_results_1 = []
    for doc_id in doc_ids:
        result = extract_document_metadata(doc_id, force=True)
        index_results_1.append(result)
        print(f"  ✓ Indexed {doc_id[:8]}: {result.get('title', 'Unknown')}")

    # Finalize KG
    kg_result_1 = finalize_knowledge_graph_from_index_results(index_results_1)

    counts_1 = get_entity_counts()
    print(f"\n  After first pass:")
    print(f"    Entities: {counts_1['entities']}")
    print(f"    Relationships: {counts_1['relationships']}")
    print(f"    Document-entity links: {counts_1['doc_entities']}")

    # Check for duplicates
    no_duplicates_1, duplicates_1 = check_for_duplicate_entities()
    assert no_duplicates_1, f"Found duplicates after first pass: {duplicates_1}"

    # Step 4: Re-index same documents (second time)
    print("\n=== Step 3: Second indexing pass (re-index same docs) ===")

    index_results_2 = []
    for doc_id in doc_ids:
        result = extract_document_metadata(doc_id, force=True)
        index_results_2.append(result)
        print(f"  ✓ Re-indexed {doc_id[:8]}: {result.get('title', 'Unknown')}")

    # Finalize KG
    kg_result_2 = finalize_knowledge_graph_from_index_results(index_results_2)

    counts_2 = get_entity_counts()
    print(f"\n  After second pass:")
    print(f"    Entities: {counts_2['entities']}")
    print(f"    Relationships: {counts_2['relationships']}")
    print(f"    Document-entity links: {counts_2['doc_entities']}")

    # Check for duplicates
    no_duplicates_2, duplicates_2 = check_for_duplicate_entities()
    assert no_duplicates_2, f"Found duplicates after second pass: {duplicates_2}"

    # Step 5: Re-index same documents (third time)
    print("\n=== Step 4: Third indexing pass (re-index again) ===")

    index_results_3 = []
    for doc_id in doc_ids:
        result = extract_document_metadata(doc_id, force=True)
        index_results_3.append(result)
        print(f"  ✓ Re-indexed {doc_id[:8]}: {result.get('title', 'Unknown')}")

    # Finalize KG
    kg_result_3 = finalize_knowledge_graph_from_index_results(index_results_3)

    counts_3 = get_entity_counts()
    print(f"\n  After third pass:")
    print(f"    Entities: {counts_3['entities']}")
    print(f"    Relationships: {counts_3['relationships']}")
    print(f"    Document-entity links: {counts_3['doc_entities']}")

    # Check for duplicates
    no_duplicates_3, duplicates_3 = check_for_duplicate_entities()
    assert no_duplicates_3, f"Found duplicates after third pass: {duplicates_3}"

    # Step 6: Verify entity counts are stable
    print("\n=== Step 5: Verifying stable entity counts ===")

    # Entity count should be stable (allowing for small variations due to LLM non-determinism)
    # But there should be NO duplicates
    assert counts_2['entities'] == counts_3['entities'], (
        f"Entity count changed between passes 2 and 3: {counts_2['entities']} -> {counts_3['entities']}"
    )

    # Print summary
    print("\n=== Summary ===")
    print(f"  Pass 1: {counts_1['entities']} entities, {counts_1['relationships']} relationships")
    print(f"  Pass 2: {counts_2['entities']} entities, {counts_2['relationships']} relationships")
    print(f"  Pass 3: {counts_3['entities']} entities, {counts_3['relationships']} relationships")
    print(f"\n  ✓ All passes completed with no duplicate entities!")

    # Verify specific examples
    print("\n=== Verifying entity uniqueness ===")
    session = get_session()

    # Check a few common entities that might appear multiple times
    common_entities = ["Dagster", "Python", "Docker", "Kubernetes", "PostgreSQL"]

    for entity_name in common_entities:
        entities = session.exec(
            select(Entity).where(Entity.name == entity_name)
        ).all()

        if entities:
            print(f"  {entity_name}: {len(entities)} instance(s)")
            assert len(entities) == 1, f"Found {len(entities)} instances of '{entity_name}', expected 1"


@pytest.mark.integration
def test_entity_linking_stability():
    """Test that entity linking is stable across re-indexing."""

    # Get test document
    from kurt.content.document import list_documents_for_indexing

    documents = list_documents_for_indexing(all_flag=True)
    if not documents:
        pytest.skip("No documents available for testing")

    test_doc = documents[0]
    doc_id = str(test_doc.id)
    doc_name = test_doc.title or test_doc.source_url or "Untitled"

    print(f"\n=== Testing with document: {doc_name} ({doc_id[:8]}) ===")

    # Clear and index first time
    clear_all_entities_and_relationships()

    result_1 = extract_document_metadata(doc_id, force=True)
    kg_result_1 = finalize_knowledge_graph_from_index_results([result_1])

    # Get linked entities
    session = get_session()
    doc_entities_1 = session.exec(
        select(DocumentEntity).where(DocumentEntity.document_id == test_doc.id)
    ).all()

    entity_ids_1 = {str(de.entity_id) for de in doc_entities_1}

    print(f"  First pass: {len(entity_ids_1)} entities linked")

    # Re-index
    result_2 = extract_document_metadata(doc_id, force=True)
    kg_result_2 = finalize_knowledge_graph_from_index_results([result_2])

    # Get linked entities again
    doc_entities_2 = session.exec(
        select(DocumentEntity).where(DocumentEntity.document_id == test_doc.id)
    ).all()

    entity_ids_2 = {str(de.entity_id) for de in doc_entities_2}

    print(f"  Second pass: {len(entity_ids_2)} entities linked")

    # Check that we're linking to the same entities (not creating new ones)
    # Allow for small variations due to LLM non-determinism, but IDs should overlap significantly
    overlap = len(entity_ids_1 & entity_ids_2)
    overlap_percentage = (overlap / len(entity_ids_1)) * 100 if entity_ids_1 else 0

    print(f"  Entity ID overlap: {overlap}/{len(entity_ids_1)} ({overlap_percentage:.1f}%)")

    # At least 70% of entities should be the same (allowing for some LLM variation)
    assert overlap_percentage >= 70, (
        f"Entity linking is unstable: only {overlap_percentage:.1f}% overlap"
    )

    print(f"  ✓ Entity linking is stable across re-indexing")
