#!/usr/bin/env python3
"""
Test script for embedding service.
This script tests the OpenAI embedding functionality with sample texts.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.embeddings.service import get_embedding_service
from app.rag.knowledge_base.pdf_loader import get_pdf_loader
from app.rag.knowledge_base.text_splitter import get_text_splitter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
import time


def main():
    console = Console()

    console.print("\n[bold cyan]Embedding Service Test[/bold cyan]\n")

    try:
        # Initialize embedding service
        console.print("[yellow]Initializing embedding service...[/yellow]")
        embedding_service = get_embedding_service(batch_size=10)

        # Test 1: Single text embedding
        console.print("\n[bold cyan]Test 1: Single Text Embedding[/bold cyan]\n")

        sample_text = """
        The Sun in Aries represents a pioneering spirit and natural leadership qualities.
        People with this placement are often energetic, enthusiastic, and quick to take action.
        They possess a strong sense of self and are not afraid to assert their independence.
        """

        console.print("[yellow]Embedding sample text...[/yellow]")
        console.print(f"[dim]Text: {sample_text.strip()[:100]}...[/dim]")

        start_time = time.time()
        embedding = embedding_service.embed_text(sample_text)
        elapsed_time = time.time() - start_time

        console.print(f"[green]✓ Embedding generated in {elapsed_time:.2f} seconds[/green]")
        console.print(f"[cyan]Embedding dimension: {len(embedding)}[/cyan]")
        console.print(f"[cyan]First 10 values: {embedding[:10]}[/cyan]")

        # Test 2: Multiple texts embedding
        console.print("\n[bold cyan]Test 2: Batch Text Embedding[/bold cyan]\n")

        sample_texts = [
            "Mars in the 1st house indicates a strong, assertive personality.",
            "Venus in Taurus seeks comfort, stability, and sensual pleasures.",
            "Mercury retrograde can bring communication challenges and delays.",
            "The Moon in Cancer is deeply emotional and nurturing.",
            "Jupiter in the 9th house expands horizons through travel and education."
        ]

        console.print(f"[yellow]Embedding {len(sample_texts)} texts...[/yellow]")

        start_time = time.time()
        embeddings = embedding_service.embed_texts(sample_texts, show_progress=False)
        elapsed_time = time.time() - start_time

        console.print(f"[green]✓ {len(embeddings)} embeddings generated in {elapsed_time:.2f} seconds[/green]")
        console.print(f"[cyan]Average time per text: {elapsed_time / len(sample_texts):.3f} seconds[/cyan]")

        # Test 3: Cosine similarity
        console.print("\n[bold cyan]Test 3: Cosine Similarity[/bold cyan]\n")

        text1 = "The Sun represents ego, identity, and core personality."
        text2 = "Solar energy reflects one's sense of self and personal power."
        text3 = "The Moon governs emotions and instinctual responses."

        console.print("[yellow]Calculating similarities...[/yellow]")

        emb1 = embedding_service.embed_text(text1)
        emb2 = embedding_service.embed_text(text2)
        emb3 = embedding_service.embed_text(text3)

        sim_1_2 = embedding_service.cosine_similarity(emb1, emb2)
        sim_1_3 = embedding_service.cosine_similarity(emb1, emb3)
        sim_2_3 = embedding_service.cosine_similarity(emb2, emb3)

        similarity_table = Table(show_header=True, header_style="bold magenta")
        similarity_table.add_column("Text Pair", style="cyan")
        similarity_table.add_column("Similarity", style="green")

        similarity_table.add_row("Sun vs Solar (related)", f"{sim_1_2:.4f}")
        similarity_table.add_row("Sun vs Moon (different)", f"{sim_1_3:.4f}")
        similarity_table.add_row("Solar vs Moon (different)", f"{sim_2_3:.4f}")

        console.print(similarity_table)
        console.print("\n[dim]Higher values indicate more similar texts[/dim]")

        # Test 4: Cache functionality
        console.print("\n[bold cyan]Test 4: Cache Performance[/bold cyan]\n")

        test_text = "Testing cache functionality with this sample text."

        console.print("[yellow]First embedding (no cache)...[/yellow]")
        start_time = time.time()
        _ = embedding_service.embed_text(test_text, use_cache=True)
        first_time = time.time() - start_time

        console.print("[yellow]Second embedding (from cache)...[/yellow]")
        start_time = time.time()
        _ = embedding_service.embed_text(test_text, use_cache=True)
        cached_time = time.time() - start_time

        console.print(f"[green]✓ First call: {first_time:.4f} seconds[/green]")
        console.print(f"[green]✓ Cached call: {cached_time:.4f} seconds[/green]")
        console.print(f"[cyan]Speedup: {first_time / cached_time:.1f}x faster[/cyan]")

        # Test 5: Document embedding
        console.print("\n[bold cyan]Test 5: Document Embedding (Small Sample)[/bold cyan]\n")

        console.print("[yellow]Loading sample documents...[/yellow]")
        pdf_loader = get_pdf_loader()
        pdf_files = pdf_loader.get_pdf_files()

        if pdf_files:
            # Load first PDF, first 2 pages
            documents = pdf_loader.load_single_pdf(pdf_files[0])
            sample_docs = documents[:2]

            console.print(f"[cyan]Loaded {len(sample_docs)} pages from {pdf_files[0].name}[/cyan]")

            # Split into chunks
            console.print("[yellow]Splitting into chunks...[/yellow]")
            text_splitter = get_text_splitter(chunk_size=500, chunk_overlap=50)
            chunks = text_splitter.split_documents(sample_docs)

            console.print(f"[cyan]Created {len(chunks)} chunks[/cyan]")

            # Embed chunks
            console.print(f"[yellow]Embedding {len(chunks)} chunks...[/yellow]")

            start_time = time.time()
            embedded_docs = embedding_service.embed_documents(
                chunks,
                use_cache=True,
                show_progress=False
            )
            elapsed_time = time.time() - start_time

            console.print(f"[green]✓ Embedded {len(embedded_docs)} chunks in {elapsed_time:.2f} seconds[/green]")
            console.print(f"[cyan]Average: {elapsed_time / len(chunks):.3f} seconds per chunk[/cyan]")

            # Show sample embedded document
            if embedded_docs:
                sample_doc = embedded_docs[0]
                console.print("\n[bold]Sample Embedded Document:[/bold]")
                console.print(Panel(
                    f"""[cyan]Text preview:[/cyan] {sample_doc['text'][:150]}...
[cyan]Embedding dim:[/cyan] {len(sample_doc['embedding'])}
[cyan]Metadata:[/cyan] {sample_doc['metadata']}""",
                    title="Document Structure",
                    border_style="blue"
                ))

        # Get cache statistics
        console.print("\n[bold cyan]Cache Statistics:[/bold cyan]\n")

        stats = embedding_service.get_embedding_stats()

        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats_table.add_row("Cached Embeddings", str(stats['cached_embeddings']))
        stats_table.add_row("Cache Size (MB)", str(stats['cache_size_mb']))
        stats_table.add_row("Model", stats['model'])
        stats_table.add_row("Dimension", str(stats['dimension']))
        stats_table.add_row("Cache Directory", stats['cache_directory'])

        console.print(stats_table)

        console.print("\n[bold green]✓ All Embedding Service Tests Completed Successfully![/bold green]\n")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
