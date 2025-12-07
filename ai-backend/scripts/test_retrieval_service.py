#!/usr/bin/env python3
# Test script for retrieval service

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.retrieval.service import get_retrieval_service
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


def main():
    console = Console()

    console.print("\n[bold cyan]Retrieval Service Test[/bold cyan]\n")

    # Sample birth chart data
    sample_chart = {
        "chart_info": {
            "name": "Test Person",
            "birth_date": "1990-07-15",
            "birth_time": "14:30"
        },
        "planets": [
            {
                "name": "Güneş",
                "name_en": "Sun",
                "sign": "Yengeç",
                "sign_en": "Cancer",
                "house": 10,
                "degree_in_sign": 22.5
            },
            {
                "name": "Ay",
                "name_en": "Moon",
                "sign": "Boğa",
                "sign_en": "Taurus",
                "house": 8,
                "degree_in_sign": 15.3
            },
            {
                "name": "Merkür",
                "name_en": "Mercury",
                "sign": "Yengeç",
                "sign_en": "Cancer",
                "house": 10,
                "degree_in_sign": 18.2
            },
            {
                "name": "Venüs",
                "name_en": "Venus",
                "sign": "İkizler",
                "sign_en": "Gemini",
                "house": 9,
                "degree_in_sign": 8.7
            },
            {
                "name": "Mars",
                "name_en": "Mars",
                "sign": "Koç",
                "sign_en": "Aries",
                "house": 7,
                "degree_in_sign": 25.1
            }
        ],
        "ascendant": {
            "sign": "Başak",
            "sign_en": "Virgo",
            "degree_in_sign": 12.4
        },
        "houses": [
            {"number": 1, "sign": "Başak", "sign_en": "Virgo"},
            {"number": 2, "sign": "Terazi", "sign_en": "Libra"},
            {"number": 3, "sign": "Akrep", "sign_en": "Scorpio"},
            {"number": 4, "sign": "Yay", "sign_en": "Sagittarius"}
        ],
        "aspects": [
            {
                "planet1": "Sun",
                "aspect": "Kare",
                "aspect_en": "Square",
                "planet2": "Mars",
                "orb": 2.6
            },
            {
                "planet1": "Moon",
                "aspect": "Üçgen",
                "aspect_en": "Trine",
                "planet2": "Venus",
                "orb": 1.2
            }
        ],
        "elements": {
            "fire": 25.0,
            "earth": 35.0,
            "air": 20.0,
            "water": 20.0
        },
        "qualities": {
            "cardinal": 30.0,
            "fixed": 40.0,
            "mutable": 30.0
        }
    }

    try:
        # Initialize retrieval service
        console.print("[yellow]Initializing retrieval service...[/yellow]")
        retrieval_service = get_retrieval_service(
            top_k=3,
            similarity_threshold=1.0  # Higher for L2 distance
        )
        console.print("[green]✓ Retrieval service initialized[/green]")

        # Test 1: Generate queries
        console.print("\n[bold cyan]Test 1: Query Generation[/bold cyan]\n")

        queries = retrieval_service.generate_queries_from_chart(sample_chart)

        console.print(f"[green]Generated {len(queries)} queries:[/green]\n")
        for i, query in enumerate(queries[:10], 1):  # Show first 10
            console.print(f"  {i}. [cyan]{query}[/cyan]")

        if len(queries) > 10:
            console.print(f"\n[dim]... and {len(queries) - 10} more queries[/dim]")

        # Test 2: Retrieve context
        console.print("\n[bold cyan]Test 2: Context Retrieval[/bold cyan]\n")

        console.print("[yellow]Retrieving relevant context from vector database...[/yellow]")
        results = retrieval_service.retrieve_context(
            sample_chart,
            max_queries=8,
            deduplicate=True
        )

        console.print(f"[green]✓ Retrieved {len(results)} relevant chunks[/green]\n")

        # Display top results
        if results:
            console.print("[bold]Top 5 Retrieved Documents:[/bold]\n")

            results_table = Table(show_header=True, header_style="bold magenta")
            results_table.add_column("#", style="dim", width=3)
            results_table.add_column("Score", style="cyan", width=8)
            results_table.add_column("Source", style="green")
            results_table.add_column("Category", style="yellow", width=15)
            results_table.add_column("Query", style="blue")

            for i, result in enumerate(results[:5], 1):
                results_table.add_row(
                    str(i),
                    f"{result['score']:.4f}",
                    result['source_file'][:30] + "...",
                    result['category'],
                    result.get('query', 'N/A')[:40] + "..."
                )

            console.print(results_table)

            # Show sample content
            console.print("\n[bold]Sample Retrieved Content:[/bold]\n")

            sample_result = results[0]
            panel_content = f"""[cyan]Source:[/cyan] {sample_result['source_file']}
[cyan]Category:[/cyan] {sample_result['category']}
[cyan]Page:[/cyan] {sample_result['page_number']}
[cyan]Score:[/cyan] {sample_result['score']:.4f}
[cyan]Query:[/cyan] {sample_result.get('query', 'N/A')}

[yellow]Content:[/yellow]
{sample_result['text'][:300]}..."""

            console.print(Panel(
                panel_content,
                title="[bold]Most Relevant Document[/bold]",
                border_style="blue"
            ))

        # Test 3: Format context
        console.print("\n[bold cyan]Test 3: Context Formatting[/bold cyan]\n")

        formatted_context = retrieval_service.format_context(results, max_chunks=5)

        console.print(f"[green]✓ Formatted context length: {len(formatted_context)} characters[/green]")
        console.print(f"[dim]Preview (first 500 chars):[/dim]\n")
        console.print(Panel(
            formatted_context[:500] + "...",
            title="[bold]Formatted Context Preview[/bold]",
            border_style="green"
        ))

        # Test 4: Category-specific retrieval
        console.print("\n[bold cyan]Test 4: Category-Specific Retrieval[/bold cyan]\n")

        console.print("[yellow]Retrieving context by category...[/yellow]")
        category_contexts = retrieval_service.get_category_specific_context(sample_chart)

        category_table = Table(show_header=True, header_style="bold magenta")
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Documents", style="green", justify="right")

        for category, docs in category_contexts.items():
            if docs:
                category_table.add_row(category, str(len(docs)))

        console.print(category_table)

        # Test 5: Single category retrieval
        console.print("\n[bold cyan]Test 5: Single Category Search[/bold cyan]\n")

        test_query = "How do planetary aspects affect personality?"
        console.print(f"[yellow]Query:[/yellow] {test_query}")
        console.print(f"[yellow]Category:[/yellow] aspects\n")

        aspect_results = retrieval_service.retrieve_by_category(
            test_query,
            'aspects',
            top_k=3
        )

        console.print(f"[green]✓ Found {len(aspect_results)} results in 'aspects' category[/green]\n")

        if aspect_results:
            for i, result in enumerate(aspect_results, 1):
                console.print(
                    f"  {i}. [cyan]{result['source_file']}[/cyan] "
                    f"(Page {result['page_number']}) - Score: {result['score']:.4f}"
                )

        # Cleanup
        console.print("\n[yellow]Disconnecting...[/yellow]")
        retrieval_service.disconnect()

        console.print("\n[bold green]✓ All Retrieval Service Tests Completed Successfully![/bold green]\n")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
