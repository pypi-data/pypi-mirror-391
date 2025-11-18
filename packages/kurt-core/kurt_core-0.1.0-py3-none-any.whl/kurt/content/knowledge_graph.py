"""
Knowledge graph extraction from documents.

This module implements the 4-stage knowledge graph extraction process:
- Stage 0: Document embedding (in fetch.py)
- Stage 1: Entity extraction with pre-resolution
- Stage 2: Create edges for EXISTING entities
- Stage 3: Resolve NEW entities
- Stage 4: Create new entities and edges

Entity Types:
- Product: Software products, tools, platforms
- Feature: Product features, capabilities
- Technology: Technologies, languages, frameworks
- Topic: General topics, concepts
- Company: Companies, organizations
- Integration: Third-party integrations

Relationship Types:
- mentions: Entity mentioned in context
- part_of: Component relationship
- integrates_with: Integration relationship
- enables: Enabling relationship
- related_to: General relationship
- depends_on: Dependency relationship
- replaces: Replacement relationship
"""

import logging
import struct
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import dspy
import numpy as np
from pydantic import BaseModel, Field
from sklearn.cluster import DBSCAN
from sqlmodel import select

from kurt.db.database import get_session
from kurt.db.models import Document, DocumentEntity, Entity, EntityRelationship

logger = logging.getLogger(__name__)

# Entity and relationship type constants
ENTITY_TYPES = ["Product", "Feature", "Technology", "Topic", "Company", "Integration"]
RELATIONSHIP_TYPES = [
    "mentions",
    "part_of",
    "integrates_with",
    "enables",
    "related_to",
    "depends_on",
    "replaces",
]


# ============================================================================
# Pydantic Models for DSPy Signatures
# ============================================================================


class EntityExtraction(BaseModel):
    """Entity extracted from document with resolution status."""

    name: str = Field(description="Entity name as mentioned in document")
    entity_type: str = Field(description=f"Entity type: {', '.join(ENTITY_TYPES)}")
    description: str = Field(description="Brief description of the entity")
    aliases: list[str] = Field(default=[], description="Alternative names for this entity")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in extraction (0.0-1.0)"
    )
    resolution_status: str = Field(
        description="Resolution status: 'EXISTING' if matches existing entity, 'NEW' if novel"
    )
    matched_entity_id: Optional[str] = Field(
        default=None, description="ID of matched existing entity (if EXISTING)"
    )


class RelationshipExtraction(BaseModel):
    """Relationship between entities extracted from document."""

    source_entity: str = Field(description="Source entity name")
    target_entity: str = Field(description="Target entity name")
    relationship_type: str = Field(
        description=f"Relationship type: {', '.join(RELATIONSHIP_TYPES)}"
    )
    context: Optional[str] = Field(
        default=None, description="Context snippet where relationship appears"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in relationship (0.0-1.0)"
    )


class EntityResolution(BaseModel):
    """Resolution decision for a group of similar NEW entities."""

    entity_names: list[str] = Field(description="Names of entities being resolved")
    resolution_decision: str = Field(
        description="Decision: 'CREATE_NEW' to create new entity, or ID of existing entity to merge with"
    )
    canonical_name: str = Field(description="Canonical name for the resolved entity")
    aliases: list[str] = Field(
        default=[], description="All aliases for the resolved entity"
    )
    reasoning: str = Field(description="Brief explanation of the resolution decision")


# ============================================================================
# DSPy Signatures
# ============================================================================


class ExtractKnowledgeGraph(dspy.Signature):
    """Extract entities and relationships from document, pre-resolving against existing entities.

    You are given a document and a list of existing entities in the knowledge base.
    Your task is to:
    1. Extract all meaningful entities mentioned in the document
    2. For each entity, determine if it matches an existing entity (mark as EXISTING) or is novel (mark as NEW)
    3. Extract relationships between entities

    For resolution:
    - Compare extracted entity name/aliases with existing entity names/aliases
    - Consider entity type - entities must be same type to match
    - If confident match (>80% similar), mark as EXISTING and provide matched_entity_id
    - If unsure or clearly different, mark as NEW
    """

    document_content: str = dspy.InputField(
        desc="Document content to extract entities from (first 5000 chars)"
    )
    existing_entities: list[dict] = dspy.InputField(
        default=[],
        desc="List of existing entities: [{id, name, type, description, aliases}, ...]",
    )
    entities: list[EntityExtraction] = dspy.OutputField(
        desc="Extracted entities with resolution status"
    )
    relationships: list[RelationshipExtraction] = dspy.OutputField(
        desc="Relationships between extracted entities"
    )


class ResolveEntityGroup(dspy.Signature):
    """Resolve a group of similar NEW entities against existing entities.

    You are given:
    1. A group of NEW entities that are semantically similar
    2. Existing entities from the knowledge base that are similar to this group

    Your task is to decide:
    - Should we CREATE_NEW entity for this group?
    - Or should we MERGE with an existing entity?

    Resolution rules:
    - If any existing entity is a clear match (same concept, just different wording), MERGE
    - If all NEW entities refer to the same novel concept not in existing entities, CREATE_NEW
    - Provide canonical name and all aliases for the resolved entity
    """

    new_entities: list[dict] = dspy.InputField(
        desc="New entities to resolve: [{name, type, description, aliases}, ...]"
    )
    existing_candidates: list[dict] = dspy.InputField(
        default=[],
        desc="Similar existing entities: [{id, name, type, description, aliases}, ...]",
    )
    resolution: EntityResolution = dspy.OutputField(
        desc="Resolution decision for this group"
    )


# ============================================================================
# Helper Functions
# ============================================================================


def _get_embedding_model() -> str:
    """Get configured embedding model from Kurt config."""
    from kurt.config import load_config

    config = load_config()
    return config.EMBEDDING_MODEL


def _generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts using configured model."""
    embedding_model = _get_embedding_model()
    embedder = dspy.Embedder(model=embedding_model)
    return embedder(texts)


def _embedding_to_bytes(embedding: list[float]) -> bytes:
    """Convert embedding list to bytes for storage."""
    return np.array(embedding, dtype=np.float32).tobytes()


def _bytes_to_embedding(embedding_bytes: bytes) -> list[float]:
    """Convert stored bytes back to embedding list."""
    return struct.unpack(f"{len(embedding_bytes)//4}f", embedding_bytes)


def _cosine_similarity(emb1: list[float], emb2: list[float]) -> float:
    """Calculate cosine similarity between two embeddings."""
    a = np.array(emb1)
    b = np.array(emb2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _get_top_entities(session, limit: int = 100) -> list[dict]:
    """Get most commonly mentioned entities for context."""
    stmt = (
        select(Entity)
        .where(Entity.source_mentions > 0)
        .order_by(Entity.source_mentions.desc())
        .limit(limit)
    )
    entities = session.exec(stmt).all()

    return [
        {
            "id": str(e.id),
            "name": e.name,
            "type": e.entity_type,
            "description": e.description or "",
            "aliases": e.aliases or [],
            "canonical_name": e.canonical_name or e.name,
        }
        for e in entities
    ]


def _search_similar_entities(
    session, entity_name: str, entity_type: str, limit: int = 20
) -> list[dict]:
    """Search for entities similar to the given name using vector search."""
    try:
        # Generate embedding for search
        embedding_vector = _generate_embeddings([entity_name])[0]
        embedding_bytes = _embedding_to_bytes(embedding_vector)

        # Use SQLite client's vector search if available
        from kurt.db.sqlite import SQLiteClient

        client = SQLiteClient()
        results = client.search_similar_entities(
            embedding_bytes, limit=limit, min_similarity=0.70
        )

        # Load entity details
        similar_entities = []
        for entity_id, similarity in results:
            entity = session.get(Entity, UUID(entity_id))
            if entity and entity.entity_type == entity_type:  # Same type only
                similar_entities.append(
                    {
                        "id": str(entity.id),
                        "name": entity.name,
                        "type": entity.entity_type,
                        "description": entity.description or "",
                        "aliases": entity.aliases or [],
                        "canonical_name": entity.canonical_name or entity.name,
                        "similarity": similarity,
                    }
                )

        return similar_entities
    except Exception as e:
        logger.debug(f"Vector search not available (fallback to simple query): {e}")
        # Fallback: get top entities of same type
        stmt = (
            select(Entity)
            .where(Entity.entity_type == entity_type)
            .order_by(Entity.source_mentions.desc())
            .limit(limit)
        )
        entities = session.exec(stmt).all()
        return [
            {
                "id": str(e.id),
                "name": e.name,
                "type": e.entity_type,
                "description": e.description or "",
                "aliases": e.aliases or [],
                "canonical_name": e.canonical_name or e.name,
            }
            for e in entities
        ]


# ============================================================================
# Stage 1: Entity Extraction with Pre-Resolution
# ============================================================================


def extract_knowledge_graph(document_id: UUID) -> dict:
    """
    Stage 1: Extract entities and relationships from document.

    Returns:
        dict with keys:
            - existing_entities: List of entity IDs marked as EXISTING
            - new_entities: List of entity dicts marked as NEW
            - relationships: List of relationship dicts
    """
    session = get_session()
    doc = session.get(Document, document_id)

    if not doc or not doc.content_path:
        raise ValueError(f"Document {document_id} not found or has no content")

    # Load document content
    from kurt.config import load_config

    config = load_config()
    content_path = config.get_absolute_sources_path() / doc.content_path
    with open(content_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Limit content length for LLM
    content_sample = content[:5000] if len(content) > 5000 else content

    # Get existing entities for context
    existing_entities = _get_top_entities(session, limit=100)

    # Run DSPy extraction signature
    extraction_module = dspy.ChainOfThought(ExtractKnowledgeGraph)
    result = extraction_module(
        document_content=content_sample, existing_entities=existing_entities
    )

    # Separate EXISTING and NEW entities
    existing_entity_ids = []
    new_entities = []

    for entity_extraction in result.entities:
        if entity_extraction.resolution_status == "EXISTING":
            if entity_extraction.matched_entity_id:
                existing_entity_ids.append(entity_extraction.matched_entity_id)
        else:  # NEW
            new_entities.append(
                {
                    "name": entity_extraction.name,
                    "type": entity_extraction.entity_type,
                    "description": entity_extraction.description,
                    "aliases": entity_extraction.aliases,
                    "confidence": entity_extraction.confidence,
                }
            )

    # Convert relationships to dicts
    relationships = [
        {
            "source_entity": rel.source_entity,
            "target_entity": rel.target_entity,
            "relationship_type": rel.relationship_type,
            "context": rel.context,
            "confidence": rel.confidence,
        }
        for rel in result.relationships
    ]

    logger.info(
        f"Stage 1 complete for doc {document_id}: "
        f"{len(existing_entity_ids)} EXISTING + {len(new_entities)} NEW entities, "
        f"{len(relationships)} relationships"
    )
    logger.debug(f"  EXISTING entities: {existing_entity_ids}")
    logger.debug(f"  NEW entities: {[e['name'] for e in new_entities]}")
    logger.debug(f"  Relationships: {[(r['source_entity'], r['relationship_type'], r['target_entity']) for r in relationships[:5]]}")

    return {
        "document_id": str(document_id),
        "existing_entities": existing_entity_ids,
        "new_entities": new_entities,
        "relationships": relationships,
    }


# ============================================================================
# Stage 2: Create Edges for EXISTING Entities
# ============================================================================


def create_existing_entity_edges(document_id: UUID, existing_entity_ids: list[str]):
    """
    Stage 2: Create document-entity edges for EXISTING entities.

    Args:
        document_id: Document UUID
        existing_entity_ids: List of entity IDs that were matched
    """
    session = get_session()

    for entity_id_str in existing_entity_ids:
        entity_id = UUID(entity_id_str)

        # Check if edge already exists
        stmt = select(DocumentEntity).where(
            DocumentEntity.document_id == document_id,
            DocumentEntity.entity_id == entity_id,
        )
        existing_edge = session.exec(stmt).first()

        if existing_edge:
            # Update mention count
            existing_edge.mention_count += 1
            existing_edge.updated_at = datetime.utcnow()
        else:
            # Create new edge
            edge = DocumentEntity(
                id=uuid4(),
                document_id=document_id,
                entity_id=entity_id,
                mention_count=1,
                confidence=0.9,  # High confidence since LLM matched it
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(edge)

        # Update entity mention count
        entity = session.get(Entity, entity_id)
        if entity:
            entity.source_mentions += 1
            entity.updated_at = datetime.utcnow()

    session.commit()
    logger.info(
        f"Stage 2 complete: Created/updated {len(existing_entity_ids)} document-entity edges for {document_id}"
    )


# ============================================================================
# Stage 3: Resolve NEW Entities
# ============================================================================


def resolve_new_entities(new_entities_batch: list[dict]) -> list[dict]:
    """
    Stage 3: Resolve NEW entities using similarity grouping and LLM verification.

    Args:
        new_entities_batch: List of NEW entity dicts from multiple documents

    Returns:
        List of resolution decisions with keys:
            - entities: List of entity names in this group
            - decision: "CREATE_NEW" or entity_id to merge with
            - canonical_name: Canonical name for entity
            - aliases: All aliases
    """
    if not new_entities_batch:
        return []

    # Generate embeddings for all NEW entities
    entity_names = [e["name"] for e in new_entities_batch]
    embeddings = _generate_embeddings(entity_names)

    # Group similar entities using DBSCAN clustering
    embeddings_array = np.array(embeddings)
    clustering = DBSCAN(eps=0.25, min_samples=1, metric="cosine")
    labels = clustering.fit_predict(embeddings_array)

    # Organize entities into groups
    groups = {}
    for idx, label in enumerate(labels):
        if label not in groups:
            groups[label] = []
        groups[label].append(new_entities_batch[idx])

    logger.info(f"Stage 3: Grouped {len(new_entities_batch)} NEW entities into {len(groups)} groups")
    logger.debug(f"  Groups: {[(gid, [e['name'] for e in ents]) for gid, ents in list(groups.items())[:3]]}")

    # Resolve each group using DSPy
    resolutions = []
    session = get_session()
    resolution_module = dspy.ChainOfThought(ResolveEntityGroup)

    for group_id, group_entities in groups.items():
        # Get similar existing entities for this group
        representative_entity = group_entities[0]
        similar_existing = _search_similar_entities(
            session,
            representative_entity["name"],
            representative_entity["type"],
            limit=10,
        )

        # Run resolution signature
        result = resolution_module(
            new_entities=group_entities, existing_candidates=similar_existing
        )

        resolutions.append(
            {
                "entities": [e["name"] for e in group_entities],
                "entity_details": group_entities,
                "decision": result.resolution.resolution_decision,
                "canonical_name": result.resolution.canonical_name,
                "aliases": result.resolution.aliases,
                "reasoning": result.resolution.reasoning,
            }
        )

    logger.info(f"Stage 3 complete: Resolved {len(groups)} entity groups")
    logger.debug(f"  Resolutions: {[(r['canonical_name'], r['decision'], len(r['entities'])) for r in resolutions]}")
    return resolutions


# ============================================================================
# Stage 4: Create New Entities and Edges
# ============================================================================


def create_entities_and_edges(
    document_id: UUID, resolutions: list[dict], relationships: list[dict]
):
    """
    Stage 4: Create new entities and all relationship edges.

    Args:
        document_id: Document UUID
        resolutions: List of resolution decisions from Stage 3
        relationships: List of relationships from Stage 1
    """
    session = get_session()

    # Map entity names to IDs (for relationship creation)
    entity_name_to_id = {}

    # Process resolutions
    for resolution in resolutions:
        if resolution["decision"] == "CREATE_NEW":
            # Create new entity
            entity_data = resolution["entity_details"][0]  # Use first as representative
            entity_embedding = _generate_embeddings([resolution["canonical_name"]])[0]

            entity = Entity(
                id=uuid4(),
                name=resolution["canonical_name"],
                entity_type=entity_data["type"],
                canonical_name=resolution["canonical_name"],
                aliases=resolution["aliases"],
                description=entity_data["description"],
                embedding=_embedding_to_bytes(entity_embedding),
                confidence_score=entity_data["confidence"],
                source_mentions=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(entity)
            session.flush()  # Get entity ID

            # Store entity_embeddings in vec0 table if available
            try:
                from sqlalchemy import text

                floats_str = ",".join(str(f) for f in entity_embedding)
                session.exec(
                    text(f"INSERT INTO entity_embeddings (entity_id, embedding) VALUES ('{entity.id}', '[{floats_str}]')")
                )
            except Exception as e:
                logger.debug(f"Could not insert into entity_embeddings: {e}")

            # Map all names in this group to this entity ID
            for ent_name in resolution["entities"]:
                entity_name_to_id[ent_name] = entity.id

            # Create document-entity edge
            edge = DocumentEntity(
                id=uuid4(),
                document_id=document_id,
                entity_id=entity.id,
                mention_count=1,
                confidence=entity_data["confidence"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(edge)

        else:  # Merge with existing
            entity_id = UUID(resolution["decision"])
            entity = session.get(Entity, entity_id)

            if entity:
                # Update aliases if new ones found
                existing_aliases = set(entity.aliases or [])
                new_aliases = set(resolution["aliases"])
                combined_aliases = list(existing_aliases | new_aliases)
                entity.aliases = combined_aliases
                entity.source_mentions += 1
                entity.updated_at = datetime.utcnow()

                # Map all names to this entity
                for ent_name in resolution["entities"]:
                    entity_name_to_id[ent_name] = entity_id

                # Create document-entity edge
                edge = DocumentEntity(
                    id=uuid4(),
                    document_id=document_id,
                    entity_id=entity_id,
                    mention_count=1,
                    confidence=0.85,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(edge)

    # Create relationships
    for rel in relationships:
        source_id = entity_name_to_id.get(rel["source_entity"])
        target_id = entity_name_to_id.get(rel["target_entity"])

        if not source_id or not target_id:
            continue  # Skip if entities not found

        # Check if relationship already exists
        stmt = select(EntityRelationship).where(
            EntityRelationship.source_entity_id == source_id,
            EntityRelationship.target_entity_id == target_id,
            EntityRelationship.relationship_type == rel["relationship_type"],
        )
        existing_rel = session.exec(stmt).first()

        if existing_rel:
            # Update evidence count
            existing_rel.evidence_count += 1
            existing_rel.updated_at = datetime.utcnow()
        else:
            # Create new relationship
            relationship = EntityRelationship(
                id=uuid4(),
                source_entity_id=source_id,
                target_entity_id=target_id,
                relationship_type=rel["relationship_type"],
                confidence=rel["confidence"],
                evidence_count=1,
                context=rel.get("context"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(relationship)

    session.commit()
    entities_created = len([r for r in resolutions if r["decision"] == "CREATE_NEW"])
    entities_merged = len(resolutions) - entities_created
    logger.info(
        f"Stage 4 complete: Created {entities_created} new entities, "
        f"merged with {entities_merged} existing entities for document {document_id}"
    )


# ============================================================================
# Main Pipeline Function
# ============================================================================


def build_knowledge_graph_for_documents(document_ids: list[UUID]):
    """
    Complete knowledge graph extraction pipeline for multiple documents.

    Stages:
    0. Document embeddings (done during fetch)
    1. Extract entities + pre-resolve (parallel per document)
    2. Create edges for EXISTING entities (immediate)
    3. Resolve NEW entities (batch)
    4. Create new entities + relationships

    Args:
        document_ids: List of document UUIDs to process
    """
    logger.info(f"🔄 Building knowledge graph for {len(document_ids)} documents")
    logger.info(f"📋 Document IDs: {[str(d)[:8] for d in document_ids]}")

    # Stage 1: Extract from all documents (can be parallelized)
    all_existing_entities = []
    all_new_entities = []
    all_relationships = []
    document_extraction_map = {}

    for idx, doc_id in enumerate(document_ids, 1):
        logger.info(f"📄 Processing document {idx}/{len(document_ids)}: {str(doc_id)[:8]}...")
        extraction = extract_knowledge_graph(doc_id)
        document_extraction_map[doc_id] = extraction

        all_existing_entities.extend(extraction["existing_entities"])
        all_new_entities.extend(extraction["new_entities"])
        all_relationships.extend(extraction["relationships"])

    logger.info(
        f"✅ Stage 1 complete: {len(all_existing_entities)} EXISTING, {len(all_new_entities)} NEW entities across all docs"
    )

    # Stage 2: Create edges for EXISTING entities
    logger.info(f"🔗 Stage 2: Creating edges for {len(all_existing_entities)} EXISTING entities...")
    for doc_id, extraction in document_extraction_map.items():
        create_existing_entity_edges(doc_id, extraction["existing_entities"])

    logger.info("✅ Stage 2 complete: Created edges for EXISTING entities")

    # Stage 3: Resolve NEW entities
    if all_new_entities:
        logger.info(f"🧩 Stage 3: Resolving {len(all_new_entities)} NEW entities...")
        resolutions = resolve_new_entities(all_new_entities)
        logger.info(f"✅ Stage 3 complete: Resolved {len(resolutions)} entity groups")

        # Stage 4: Create new entities and edges
        logger.info(f"💾 Stage 4: Creating entities and relationships...")
        for doc_id, extraction in document_extraction_map.items():
            create_entities_and_edges(
                doc_id, resolutions, extraction["relationships"]
            )
        logger.info("✅ Stage 4 complete: Created new entities and relationships")
    else:
        logger.info("ℹ️  No NEW entities to resolve, skipping stages 3-4")

    logger.info(f"🎉 Knowledge graph build complete for {len(document_ids)} documents!")
