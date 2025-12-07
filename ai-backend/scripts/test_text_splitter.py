#!/usr/bin/env python3
"""
Test script for text splitter service.
This script tests the chunking functionality with PDF documents.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.knowledge_base.pdf_loader import get_pdf_loader
from app.rag.knowledge_base.text_splitter import get_text_splitter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint


def main():
    console = Console()

    console.print("\n[bold cyan]Text Splitter Service Test[/bold cyan]\n")

    try:
        # Initialize services
        console.print("[yellow]Initializing PDF loader...[/yellow]")
        pdf_loader = get_pdf_loader()

        console.print("[yellow]Initializing text splitter (chunk_size=1024, overlap=200)...[/yellow]")
        text_splitter = get_text_splitter(chunk_size=1024, chunk_overlap=200)

        # Load a sample PDF
        console.print("\n[yellow]Loading sample PDF...[/yellow]")
        pdf_files = pdf_loader.get_pdf_files()

        if not pdf_files:
            console.print("[red]No PDF files found![/red]")
            return

        # Load first PDF as test
        test_pdf = pdf_files[0]
        console.print(f"[green]Using: {test_pdf.name}[/green]")
        documents = pdf_loader.load_single_pdf(test_pdf)

        # Take first 5 pages for testing
        sample_docs = documents[:5]
        console.print(f"[cyan]Testing with first {len(sample_docs)} pages[/cyan]")

        # Split documents into chunks
        console.print("\n[yellow]Splitting documents into chunks...[/yellow]")
        chunks = text_splitter.split_documents(sample_docs)

        # Get statistics
        stats = text_splitter.get_chunk_statistics(chunks)

        # Display statistics
        console.print("\n[bold cyan]Chunking Statistics:[/bold cyan]\n")

        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats_table.add_row("Original Pages", str(len(sample_docs)))
        stats_table.add_row("Total Chunks", str(stats['total_chunks']))
        stats_table.add_row("Total Characters", f"{stats['total_characters']:,}")
        stats_table.add_row("Avg Chunk Size", f"{stats['avg_chunk_size']:.2f}")
        stats_table.add_row("Min Chunk Size", str(stats['min_chunk_size']))
        stats_table.add_row("Max Chunk Size", str(stats['max_chunk_size']))
        stats_table.add_row("Configured Chunk Size", str(stats['configured_chunk_size']))
        stats_table.add_row("Configured Overlap", str(stats['configured_overlap']))

        console.print(stats_table)

        # Display chunk previews
        console.print("\n[bold cyan]Chunk Previews:[/bold cyan]\n")

        previews = text_splitter.preview_chunks(chunks, num_previews=3, preview_length=150)

        for i, preview in enumerate(previews, 1):
            panel_content = f"""[cyan]Source:[/cyan] {preview['source_file']}
[cyan]Page:[/cyan] {preview['page_number']}
[cyan]Chunk ID:[/cyan] {preview['chunk_id']}
[cyan]Size:[/cyan] {preview['chunk_size']} characters

[yellow]Content Preview:[/yellow]
{preview['content_preview']}..."""

            console.print(Panel(
                panel_content,
                title=f"[bold]Chunk {i}[/bold]",
                border_style="blue"
            ))

        # Test with all PDFs
        console.print("\n[yellow]Now testing with ALL PDFs...[/yellow]")
        all_documents = pdf_loader.load_all_pdfs_flat()
        console.print(f"[cyan]Loaded {len(all_documents)} total pages[/cyan]")

        console.print("[yellow]Chunking all documents (this may take a moment)...[/yellow]")
        all_chunks = text_splitter.split_documents(all_documents)

        # Get full statistics
        full_stats = text_splitter.get_chunk_statistics(all_chunks)

        console.print("\n[bold cyan]Full Corpus Statistics:[/bold cyan]\n")

        full_stats_table = Table(show_header=True, header_style="bold magenta")
        full_stats_table.add_column("Metric", style="cyan")
        full_stats_table.add_column("Value", style="green")

        full_stats_table.add_row("Total Pages", str(len(all_documents)))
        full_stats_table.add_row("Total Chunks", str(full_stats['total_chunks']))
        full_stats_table.add_row("Total Characters", f"{full_stats['total_characters']:,}")
        full_stats_table.add_row("Avg Chunk Size", f"{full_stats['avg_chunk_size']:.2f}")
        full_stats_table.add_row("Chunks per Page Ratio", f"{full_stats['total_chunks'] / len(all_documents):.2f}")

        console.print(full_stats_table)

        # Display chunks by source
        console.print("\n[bold cyan]Chunks by Source File:[/bold cyan]\n")

        source_table = Table(show_header=True, header_style="bold magenta")
        source_table.add_column("Source File", style="cyan")
        source_table.add_column("Chunks", style="green")

        for source, count in sorted(
            full_stats['chunks_by_source'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            source_table.add_row(source, str(count))

        console.print(source_table)

        console.print("\n[bold green]✓ Text Splitter Test Completed Successfully![/bold green]\n")

        # Return the chunks for potential use
        return all_chunks

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    chunks = main()
