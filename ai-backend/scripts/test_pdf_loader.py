#!/usr/bin/env python3
"""
Test script for PDF loader service.
This script tests the PDF loading functionality and displays statistics.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.knowledge_base.pdf_loader import get_pdf_loader
from rich.console import Console
from rich.table import Table
from rich import print as rprint


def main():
    console = Console()

    console.print("\n[bold cyan]PDF Loader Service Test[/bold cyan]\n")

    try:
        # Initialize PDF loader
        console.print("[yellow]Initializing PDF loader...[/yellow]")
        loader = get_pdf_loader()

        # Get PDF files
        console.print("\n[yellow]Scanning for PDF files...[/yellow]")
        pdf_files = loader.get_pdf_files()

        if not pdf_files:
            console.print("[red]No PDF files found![/red]")
            return

        # Display found PDFs
        console.print(f"\n[green]Found {len(pdf_files)} PDF files:[/green]")
        for i, pdf_path in enumerate(pdf_files, 1):
            console.print(f"  {i}. {pdf_path.name}")

        # Load a single PDF as test
        console.print("\n[yellow]Testing single PDF load...[/yellow]")
        test_pdf = pdf_files[0]
        documents = loader.load_single_pdf(test_pdf)

        console.print(f"[green]✓ Successfully loaded {test_pdf.name}[/green]")
        console.print(f"  Pages: {len(documents)}")
        console.print(f"  First page preview (200 chars):")
        preview = documents[0].page_content[:200].replace('\n', ' ')
        console.print(f"  [dim]{preview}...[/dim]")

        # Display metadata
        console.print("\n[cyan]Metadata sample:[/cyan]")
        metadata = documents[0].metadata
        for key, value in metadata.items():
            console.print(f"  {key}: {value}")

        # Get statistics
        console.print("\n[yellow]Loading all PDFs and calculating statistics...[/yellow]")
        stats = loader.get_document_stats()

        # Display statistics in a table
        console.print("\n[bold cyan]Document Statistics:[/bold cyan]\n")

        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats_table.add_row("Total PDF Files", str(stats['pdf_files']))
        stats_table.add_row("Total Pages", str(stats['total_documents']))
        stats_table.add_row("Total Characters", f"{stats['total_characters']:,}")
        stats_table.add_row(
            "Avg Chars/Page",
            f"{stats['average_chars_per_page']:,.2f}"
        )

        console.print(stats_table)

        # Display category breakdown
        console.print("\n[bold cyan]Documents by Category:[/bold cyan]\n")

        category_table = Table(show_header=True, header_style="bold magenta")
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Pages", style="green")

        for category, count in sorted(
            stats['documents_by_category'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            category_table.add_row(category, str(count))

        console.print(category_table)

        console.print("\n[bold green]✓ PDF Loader Test Completed Successfully![/bold green]\n")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
