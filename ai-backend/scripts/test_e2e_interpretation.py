#!/usr/bin/env python3
"""
End-to-end test for the birth chart interpretation pipeline.
This script tests the complete flow from birth chart data to AI interpretation.

Usage:
    python scripts/test_e2e_interpretation.py

Requirements:
    - Milvus must be running (docker-compose up -d milvus-standalone)
    - Knowledge base must be ingested (python scripts/ingest_pdfs.py)
    - OpenAI API key must be set in .env
"""

import sys
from pathlib import Path
import asyncio
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

console = Console()


# Sample birth chart data for testing
SAMPLE_CHART_DATA = {
    "chart_info": {
        "name": "Test User",
        "birth_date": "1990-05-15",
        "birth_time": "10:30",
        "birth_datetime_local": "1990-05-15T10:30:00",
        "birth_datetime_utc": "1990-05-15T07:30:00Z",
        "location": {
            "city": "Istanbul",
            "country": "Turkey",
            "latitude": 41.0082,
            "longitude": 28.9784,
            "timezone": "Europe/Istanbul"
        },
        "house_system": "Placidus",
        "julian_day": 2448028.8125
    },
    "planets": [
        {
            "name": "Gunes",
            "name_en": "Sun",
            "symbol": "\u2609",
            "longitude": 54.5,
            "latitude": 0.0,
            "distance": 1.011,
            "speed": 0.957,
            "speed_display": "00\u00b057'25\"",
            "sign": "Boga",
            "sign_en": "Taurus",
            "sign_symbol": "\u2649",
            "degree_in_sign": 24.5,
            "degree_display": "24\u00b030'",
            "house": 10,
            "retrograde": False,
            "dignity": "neutral"
        },
        {
            "name": "Ay",
            "name_en": "Moon",
            "symbol": "\u263d",
            "longitude": 185.3,
            "latitude": 3.8,
            "distance": 0.0025,
            "speed": 12.8,
            "speed_display": "12\u00b048'00\"",
            "sign": "Terazi",
            "sign_en": "Libra",
            "sign_symbol": "\u264e",
            "degree_in_sign": 5.3,
            "degree_display": "05\u00b018'",
            "house": 3,
            "retrograde": False,
            "dignity": "neutral"
        },
        {
            "name": "Merkur",
            "name_en": "Mercury",
            "symbol": "\u263f",
            "longitude": 42.1,
            "latitude": -1.2,
            "distance": 0.68,
            "speed": 2.1,
            "speed_display": "02\u00b006'00\"",
            "sign": "Boga",
            "sign_en": "Taurus",
            "sign_symbol": "\u2649",
            "degree_in_sign": 12.1,
            "degree_display": "12\u00b006'",
            "house": 10,
            "retrograde": False,
            "dignity": "neutral"
        },
        {
            "name": "Venus",
            "name_en": "Venus",
            "symbol": "\u2640",
            "longitude": 28.5,
            "latitude": 1.5,
            "distance": 1.45,
            "speed": 1.15,
            "speed_display": "01\u00b009'00\"",
            "sign": "Koc",
            "sign_en": "Aries",
            "sign_symbol": "\u2648",
            "degree_in_sign": 28.5,
            "degree_display": "28\u00b030'",
            "house": 9,
            "retrograde": False,
            "dignity": "detriment"
        },
        {
            "name": "Mars",
            "name_en": "Mars",
            "symbol": "\u2642",
            "longitude": 355.8,
            "latitude": 0.8,
            "distance": 2.3,
            "speed": 0.65,
            "speed_display": "00\u00b039'00\"",
            "sign": "Balik",
            "sign_en": "Pisces",
            "sign_symbol": "\u2653",
            "degree_in_sign": 25.8,
            "degree_display": "25\u00b048'",
            "house": 8,
            "retrograde": False,
            "dignity": "neutral"
        },
        {
            "name": "Jupiter",
            "name_en": "Jupiter",
            "symbol": "\u2643",
            "longitude": 96.2,
            "latitude": 0.3,
            "distance": 5.8,
            "speed": 0.08,
            "speed_display": "00\u00b004'48\"",
            "sign": "Yengec",
            "sign_en": "Cancer",
            "sign_symbol": "\u264b",
            "degree_in_sign": 6.2,
            "degree_display": "06\u00b012'",
            "house": 12,
            "retrograde": False,
            "dignity": "exalted"
        },
        {
            "name": "Saturn",
            "name_en": "Saturn",
            "symbol": "\u2644",
            "longitude": 291.5,
            "latitude": 1.8,
            "distance": 10.2,
            "speed": 0.03,
            "speed_display": "00\u00b001'48\"",
            "sign": "Oglak",
            "sign_en": "Capricorn",
            "sign_symbol": "\u2651",
            "degree_in_sign": 21.5,
            "degree_display": "21\u00b030'",
            "house": 6,
            "retrograde": False,
            "dignity": "ruler"
        }
    ],
    "houses": [
        {"number": 1, "name": "1. Ev - Benlik", "cusp_longitude": 118.0, "sign": "Aslan", "sign_en": "Leo", "sign_symbol": "\u264c", "degree_in_sign": 28.0, "degree_display": "28\u00b000'"},
        {"number": 2, "name": "2. Ev - Degerler", "cusp_longitude": 145.0, "sign": "Basak", "sign_en": "Virgo", "sign_symbol": "\u264d", "degree_in_sign": 25.0, "degree_display": "25\u00b000'"},
        {"number": 3, "name": "3. Ev - Iletisim", "cusp_longitude": 175.0, "sign": "Terazi", "sign_en": "Libra", "sign_symbol": "\u264e", "degree_in_sign": 25.0, "degree_display": "25\u00b000'"},
        {"number": 4, "name": "4. Ev - Ev ve Aile", "cusp_longitude": 208.0, "sign": "Akrep", "sign_en": "Scorpio", "sign_symbol": "\u264f", "degree_in_sign": 28.0, "degree_display": "28\u00b000'"},
        {"number": 5, "name": "5. Ev - Yaraticilik", "cusp_longitude": 242.0, "sign": "Yay", "sign_en": "Sagittarius", "sign_symbol": "\u2650", "degree_in_sign": 2.0, "degree_display": "02\u00b000'"},
        {"number": 6, "name": "6. Ev - Saglik", "cusp_longitude": 277.0, "sign": "Oglak", "sign_en": "Capricorn", "sign_symbol": "\u2651", "degree_in_sign": 7.0, "degree_display": "07\u00b000'"},
        {"number": 7, "name": "7. Ev - Iliskiler", "cusp_longitude": 298.0, "sign": "Kova", "sign_en": "Aquarius", "sign_symbol": "\u2652", "degree_in_sign": 28.0, "degree_display": "28\u00b000'"},
        {"number": 8, "name": "8. Ev - Donusum", "cusp_longitude": 325.0, "sign": "Balik", "sign_en": "Pisces", "sign_symbol": "\u2653", "degree_in_sign": 25.0, "degree_display": "25\u00b000'"},
        {"number": 9, "name": "9. Ev - Felsefe", "cusp_longitude": 355.0, "sign": "Koc", "sign_en": "Aries", "sign_symbol": "\u2648", "degree_in_sign": 25.0, "degree_display": "25\u00b000'"},
        {"number": 10, "name": "10. Ev - Kariyer", "cusp_longitude": 28.0, "sign": "Boga", "sign_en": "Taurus", "sign_symbol": "\u2649", "degree_in_sign": 28.0, "degree_display": "28\u00b000'"},
        {"number": 11, "name": "11. Ev - Topluluk", "cusp_longitude": 62.0, "sign": "Ikizler", "sign_en": "Gemini", "sign_symbol": "\u264a", "degree_in_sign": 2.0, "degree_display": "02\u00b000'"},
        {"number": 12, "name": "12. Ev - Manevi", "cusp_longitude": 97.0, "sign": "Yengec", "sign_en": "Cancer", "sign_symbol": "\u264b", "degree_in_sign": 7.0, "degree_display": "07\u00b000'"}
    ],
    "aspects": [
        {"planet1": "Sun", "aspect": "Kavusma", "aspect_en": "Conjunction", "aspect_symbol": "\u260c", "planet2": "Mercury", "orb": 2.4, "angle": 0, "nature": "neutral"},
        {"planet1": "Moon", "aspect": "Kare", "aspect_en": "Square", "aspect_symbol": "\u25a1", "planet2": "Jupiter", "orb": 0.9, "angle": 90, "nature": "challenging"},
        {"planet1": "Venus", "aspect": "Sekstil", "aspect_en": "Sextile", "aspect_symbol": "\u26b9", "planet2": "Mars", "orb": 2.7, "angle": 60, "nature": "harmonious"},
        {"planet1": "Jupiter", "aspect": "Karsi", "aspect_en": "Opposition", "aspect_symbol": "\u260d", "planet2": "Saturn", "orb": 4.7, "angle": 180, "nature": "challenging"},
        {"planet1": "Sun", "aspect": "Ucgen", "aspect_en": "Trine", "aspect_symbol": "\u25b3", "planet2": "Saturn", "orb": 3.0, "angle": 120, "nature": "harmonious"}
    ],
    "ascendant": {
        "name": "Yukselen",
        "name_en": "Ascendant",
        "sign": "Aslan",
        "sign_en": "Leo",
        "sign_symbol": "\u264c",
        "degree_in_sign": 28.0,
        "degree_display": "28\u00b000'"
    },
    "elements": {
        "fire": 20.0,
        "earth": 40.0,
        "air": 20.0,
        "water": 20.0
    },
    "qualities": {
        "cardinal": 30.0,
        "fixed": 35.0,
        "mutable": 35.0
    }
}


async def run_e2e_test():
    """Run end-to-end interpretation test."""
    console.print("\n[bold cyan]End-to-End RAG Interpretation Test[/bold cyan]\n")

    start_time = time.time()

    try:
        # Step 1: Initialize RAG services
        console.print("[yellow]Step 1: Initializing RAG services...[/yellow]")

        from app.rag import get_rag_service_manager

        manager = get_rag_service_manager()
        init_success = await manager.initialize()

        if not init_success:
            console.print("[red]Failed to initialize RAG services[/red]")
            console.print("[dim]Make sure Milvus is running and knowledge base is ingested[/dim]")
            return False

        console.print("[green]\u2713 RAG services initialized[/green]")

        # Step 2: Get retrieval service
        console.print("\n[yellow]Step 2: Creating retrieval service...[/yellow]")

        retrieval = manager.get_retrieval_service(
            top_k=5,
            similarity_threshold=1.5  # L2 distance threshold
        )

        console.print("[green]\u2713 Retrieval service created[/green]")

        # Step 3: Generate queries from chart data
        console.print("\n[yellow]Step 3: Generating queries from birth chart...[/yellow]")

        queries = retrieval.generate_queries_from_chart(SAMPLE_CHART_DATA)
        console.print(f"[green]\u2713 Generated {len(queries)} queries[/green]")

        # Show some queries
        console.print("[dim]Sample queries:[/dim]")
        for q in queries[:5]:
            console.print(f"  - {q}")

        # Step 4: Retrieve context
        console.print("\n[yellow]Step 4: Retrieving context from knowledge base...[/yellow]")

        results = retrieval.retrieve_context(
            SAMPLE_CHART_DATA,
            max_queries=10,
            deduplicate=True
        )

        console.print(f"[green]\u2713 Retrieved {len(results)} relevant chunks[/green]")

        if results:
            # Show retrieval stats
            stats_table = Table(title="Retrieval Results")
            stats_table.add_column("Source", style="cyan")
            stats_table.add_column("Category", style="green")
            stats_table.add_column("Score", style="yellow", justify="right")

            for r in results[:5]:
                stats_table.add_row(
                    r.get("source_file", "unknown")[:30],
                    r.get("category", "unknown"),
                    f"{r.get('score', 0):.4f}"
                )

            console.print(stats_table)

        # Step 5: Format context
        console.print("\n[yellow]Step 5: Formatting context for LLM...[/yellow]")

        context = retrieval.format_context(results, max_chunks=10)
        console.print(f"[green]\u2713 Context formatted ({len(context)} characters)[/green]")

        # Step 6: Generate interpretation
        console.print("\n[yellow]Step 6: Generating AI interpretation...[/yellow]")
        console.print("[dim]This may take 30-60 seconds...[/dim]")

        generation = manager.generation_service
        interpretation = generation.generate_interpretation(
            chart_data=SAMPLE_CHART_DATA,
            context=context,
            language="tr"
        )

        console.print("[green]\u2713 Interpretation generated[/green]")

        # Calculate total time
        total_time = time.time() - start_time

        # Display results
        console.print("\n" + "=" * 80 + "\n")
        console.print(Panel(
            f"""[bold green]E2E Test Completed Successfully![/bold green]

Total Time: {total_time:.2f} seconds
Queries Generated: {len(queries)}
Chunks Retrieved: {len(results)}
Interpretation Length: {len(interpretation)} characters
""",
            title="[bold]Test Results[/bold]",
            border_style="green"
        ))

        # Show interpretation preview
        console.print("\n[bold cyan]Interpretation Preview:[/bold cyan]\n")
        console.print(Panel(
            Markdown(interpretation[:2000] + "..." if len(interpretation) > 2000 else interpretation),
            title="[bold]Generated Interpretation[/bold]",
            border_style="cyan"
        ))

        # Cleanup
        await manager.shutdown()
        console.print("\n[green]\u2713 Services shut down successfully[/green]")

        return True

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        return False


def main():
    """Main entry point."""
    console.print(Panel(
        """[bold]End-to-End RAG Interpretation Test[/bold]

This test will:
1. Initialize RAG services (connect to Milvus)
2. Generate search queries from birth chart data
3. Retrieve relevant context from the knowledge base
4. Generate an AI interpretation using GPT-4

[yellow]Prerequisites:[/yellow]
- Milvus running (docker-compose up -d milvus-standalone)
- Knowledge base ingested (python scripts/ingest_pdfs.py)
- OpenAI API key configured in .env
""",
        title="[bold cyan]Test Information[/bold cyan]",
        border_style="blue"
    ))

    success = asyncio.run(run_e2e_test())

    if success:
        console.print("\n[bold green]All tests passed![/bold green]\n")
        sys.exit(0)
    else:
        console.print("\n[bold red]Test failed![/bold red]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
