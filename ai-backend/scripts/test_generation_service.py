#!/usr/bin/env python3
# Test script for generation service and full RAG pipeline

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.retrieval.service import get_retrieval_service
from app.rag.generation.service import get_generation_service
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown


def main():
    console = Console()

    console.print("\n[bold cyan]Generation Service & Full RAG Pipeline Test[/bold cyan]\n")

    # Sample birth chart data
    sample_chart = {
        "chart_info": {
            "name": "Ayşe Yılmaz",
            "birth_date": "1992-03-21",
            "birth_time": "10:30",
            "birth_datetime_local": "1992-03-21 10:30:00",
            "birth_datetime_utc": "1992-03-21 08:30:00"
        },
        "planets": [
            {
                "name": "Güneş",
                "name_en": "Sun",
                "sign": "Koç",
                "sign_en": "Aries",
                "house": 7,
                "degree_in_sign": 0.5,
                "retrograde": False
            },
            {
                "name": "Ay",
                "name_en": "Moon",
                "sign": "Balık",
                "sign_en": "Pisces",
                "house": 6,
                "degree_in_sign": 18.3,
                "retrograde": False
            },
            {
                "name": "Merkür",
                "name_en": "Mercury",
                "sign": "Koç",
                "sign_en": "Aries",
                "house": 7,
                "degree_in_sign": 15.2,
                "retrograde": False
            },
            {
                "name": "Venüs",
                "name_en": "Venus",
                "sign": "Boğa",
                "sign_en": "Taurus",
                "house": 8,
                "degree_in_sign": 22.1,
                "retrograde": False
            },
            {
                "name": "Mars",
                "name_en": "Mars",
                "sign": "Koç",
                "sign_en": "Aries",
                "house": 7,
                "degree_in_sign": 8.9,
                "retrograde": False
            }
        ],
        "ascendant": {
            "sign": "Terazi",
            "sign_en": "Libra",
            "degree_in_sign": 15.7
        },
        "houses": [
            {"number": 1, "sign": "Terazi", "sign_en": "Libra"},
            {"number": 2, "sign": "Akrep", "sign_en": "Scorpio"},
            {"number": 3, "sign": "Yay", "sign_en": "Sagittarius"},
            {"number": 4, "sign": "Oğlak", "sign_en": "Capricorn"}
        ],
        "aspects": [
            {
                "planet1": "Sun",
                "aspect": "Konjünksiyon",
                "aspect_en": "Conjunction",
                "planet2": "Mars",
                "orb": 1.4,
                "nature": "neutral"
            },
            {
                "planet1": "Moon",
                "aspect": "Sekstil",
                "aspect_en": "Sextile",
                "planet2": "Venus",
                "orb": 2.1,
                "nature": "harmonious"
            }
        ],
        "elements": {
            "fire": 40.0,
            "earth": 20.0,
            "air": 15.0,
            "water": 25.0
        },
        "qualities": {
            "cardinal": 50.0,
            "fixed": 30.0,
            "mutable": 20.0
        }
    }

    try:
        # Step 1: Initialize services
        console.print("[yellow]Step 1: Initializing services...[/yellow]")
        retrieval_service = get_retrieval_service(top_k=5, similarity_threshold=1.0)
        generation_service = get_generation_service()
        console.print("[green]✓ Services initialized[/green]")

        # Step 2: Retrieve context
        console.print("\n[yellow]Step 2: Retrieving relevant context from knowledge base...[/yellow]")

        results = retrieval_service.retrieve_context(
            sample_chart,
            max_queries=8,
            deduplicate=True
        )

        console.print(f"[green]✓ Retrieved {len(results)} relevant documents[/green]")

        # Format context
        context = retrieval_service.format_context(results, max_chunks=15)
        console.print(f"[dim]Context length: {len(context)} characters[/dim]")

        # Step 3: Generate interpretation
        console.print("\n[yellow]Step 3: Generating interpretation with GPT-4o-mini...[/yellow]")
        console.print("[dim]This may take 10-30 seconds...[/dim]\n")

        interpretation = generation_service.generate_interpretation(
            chart_data=sample_chart,
            context=context,
            language="tr"
        )

        console.print("[green]✓ Interpretation generated successfully![/green]")

        # Display interpretation
        console.print("\n[bold cyan]Generated Interpretation:[/bold cyan]\n")

        # Render as markdown
        md = Markdown(interpretation)
        console.print(Panel(
            md,
            title="[bold]Doğum Haritası Yorumu[/bold]",
            border_style="blue",
            padding=(1, 2)
        ))

        # Show interpretation stats
        console.print("\n[bold cyan]Interpretation Statistics:[/bold cyan]\n")
        console.print(f"  • Total characters: {len(interpretation):,}")
        console.print(f"  • Total words: {len(interpretation.split()):,}")
        console.print(f"  • Lines: {len(interpretation.splitlines())}")

        # Cleanup
        retrieval_service.disconnect()

        console.print("\n[bold green]✓ All Generation Service Tests Completed Successfully![/bold green]\n")

        console.print("[bold]The full RAG pipeline is working:[/bold]")
        console.print("  1. ✓ PDF Knowledge Base Loaded")
        console.print("  2. ✓ Context Retrieval from Milvus")
        console.print("  3. ✓ AI-Powered Interpretation Generation")
        console.print("\n[cyan]Your astrology interpretation system is ready to use![/cyan]\n")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
