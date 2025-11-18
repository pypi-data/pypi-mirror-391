"""Shared display utilities for content commands."""

from rich.console import Console


def display_knowledge_graph(kg: dict, console: Console, title: str = "Knowledge Graph"):
    """
    Display knowledge graph in a consistent format.

    Args:
        kg: Knowledge graph data with stats, entities, and relationships
        console: Rich Console instance for output
        title: Title to display (default: "Knowledge Graph")
    """
    if not kg:
        return

    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print(f"[dim]{'─' * 60}[/dim]")

    # Stats
    console.print(f"[bold]Entities:[/bold] {kg['stats']['entity_count']}")
    console.print(f"[bold]Relationships:[/bold] {kg['stats']['relationship_count']}")

    if kg['stats']['entity_count'] > 0:
        console.print(
            f"[bold]Avg Entity Confidence:[/bold] {kg['stats']['avg_entity_confidence']:.2f}"
        )

    # Top entities
    if kg['entities']:
        console.print(f"\n[bold]Top Entities:[/bold]")
        for entity in kg['entities'][:10]:
            aliases_str = (
                f" (aliases: {', '.join(entity['aliases'][:2])})" if entity['aliases'] else ""
            )
            console.print(f"  • {entity['name']} [{entity['type']}]{aliases_str}")
            console.print(
                f"    [dim]Confidence: {entity['confidence']:.2f}, "
                f"Mentions: {entity['mentions_in_doc']}[/dim]"
            )
            if entity.get('mention_context'):
                quote = (
                    entity['mention_context'][:100] + "..."
                    if len(entity['mention_context']) > 100
                    else entity['mention_context']
                )
                console.print(f"    [dim italic]\"{quote}\"[/dim italic]")

    # Relationships
    if kg['relationships']:
        console.print(f"\n[bold]Relationships:[/bold]")
        for rel in kg['relationships'][:10]:
            console.print(
                f"  • {rel['source_entity']} --[{rel['relationship_type']}]--> "
                f"{rel['target_entity']}"
            )
            console.print(f"    [dim]Confidence: {rel['confidence']:.2f}[/dim]")
            if rel.get('context'):
                context = (
                    rel['context'][:100] + "..." if len(rel['context']) > 100 else rel['context']
                )
                console.print(f"    [dim italic]\"{context}\"[/dim italic]")
