"""Data models for document indexing."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from kurt.db.models import ContentType


class DocumentMetadataOutput(BaseModel):
    """Metadata extracted from document content."""

    content_type: ContentType
    extracted_title: Optional[str] = None
    primary_topics: list[str] = []
    tools_technologies: list[str] = []
    has_code_examples: bool = False
    has_step_by_step_procedures: bool = False
    has_narrative_structure: bool = False


class EntityExtraction(BaseModel):
    """Entity extracted from document with resolution status."""

    name: str
    entity_type: str  # Product, Feature, Technology, Topic, Company, Integration
    description: str
    aliases: list[str] = []
    confidence: float  # 0.0-1.0
    resolution_status: str  # "EXISTING" or "NEW"
    matched_entity_index: Optional[int] = None  # If EXISTING, the index from existing_entities list
    quote: Optional[str] = None  # Exact quote/context where entity is mentioned (50-200 chars)


class RelationshipExtraction(BaseModel):
    """Relationship between entities extracted from document."""

    source_entity: str
    target_entity: str
    relationship_type: str  # mentions, part_of, integrates_with, etc.
    context: Optional[str] = None
    confidence: float  # 0.0-1.0
