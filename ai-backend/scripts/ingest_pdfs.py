#!/usr/bin/env python3
# Main script to ingest all PDF documents into Milvus vector database
# This script loads, chunks, embeds, and stores all astrology knowledge base PDFs

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.knowledge_base.pdf_loader import get_astrology_pdf_loader
from app.rag.knowledge_base.text_splitter import get_astrology_text_splitter
from app.rag.embeddings.service import get_astrology_embedding_service
from app.rag.knowledge_base.vector_store import get_vector_store
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    TimeElapsedColumn
)
import argparse


def main():
    console = Console()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Ingest PDF documents into Milvus vector database"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1024,
        help="Chunk size in characters (default: 1024)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Chunk overlap in characters (default: 200)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Embedding batch size (default: 50)"
    )
    parser.add_argument(
        "--drop-existing",
        action="store_true",
        help="Drop existing collection before ingestion"
    )
    parser.add_argument(
        "--skip-cache",
        action="store_true",
        help="Skip embedding cache (force re-embedding)"
    )

    args = parser.parse_args()

    console.print("\n[bold cyan]PDF Ingestion Pipeline[/bold cyan]\n")
    console.print(Panel(
        f"""[cyan]Configuration:[/cyan]
• Chunk Size: {args.chunk_size} characters
• Chunk Overlap: {args.chunk_overlap} characters
• Embedding Batch Size: {args.batch_size}
• Drop Existing Collection: {args.drop_existing}
• Use Cache: {not args.skip_cache}""",
        title="[bold]Settings[/bold]",
        border_style="blue"
    ))

    start_time = time.time()

    try:
        # Initialize services
        console.print("\n[yellow]Step 1: Initializing services...[/yellow]")
        pdf_loader = get_astrology_pdf_loader(pdf_directory="./app/rag/knowledge_base/astrology-documents")
        text_splitter = get_astrology_text_splitter(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
        embedding_service = get_astrology_embedding_service(batch_size=args.batch_size)
        vector_store = get_vector_store()

        console.print("[green]✓ Services initialized[/green]")

        # Connect to Milvus
        console.print("\n[yellow]Step 2: Connecting to Milvus...[/yellow]")
        vector_store.connect()
        console.print(f"[green]✓ Connected to Milvus at {vector_store.host}:{vector_store.port}[/green]")

        # Create or load collection
        console.print("\n[yellow]Step 3: Setting up collection...[/yellow]")
        vector_store.create_collection(drop_existing=args.drop_existing)
        vector_store.create_index()
        console.print(f"[green]✓ Collection '{vector_store.collection_name}' ready[/green]")

        # Load PDFs
        console.print("\n[yellow]Step 4: Loading PDF files...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:

            task = progress.add_task("[cyan]Loading PDFs...", total=None)
            all_documents = pdf_loader.load_all_pdfs_flat()
            progress.update(task, completed=True)

        console.print(f"[green]✓ Loaded {len(all_documents)} pages from {len(pdf_loader.get_pdf_files())} PDF files[/green]")

        # Display PDF statistics
        pdf_stats_table = Table(show_header=True, header_style="bold magenta")
        pdf_stats_table.add_column("PDF File", style="cyan")
        pdf_stats_table.add_column("Pages", style="green", justify="right")

        pdf_counts = {}
        for doc in all_documents:
            source = doc.metadata.get('source_file', 'unknown')
            pdf_counts[source] = pdf_counts.get(source, 0) + 1

        for pdf_name, count in sorted(pdf_counts.items(), key=lambda x: x[1], reverse=True):
            pdf_stats_table.add_row(pdf_name, str(count))

        console.print("\n", pdf_stats_table)

        # Split into chunks
        console.print("\n[yellow]Step 5: Splitting documents into chunks...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:

            task = progress.add_task("[cyan]Chunking...", total=None)
            chunks = text_splitter.split_documents(all_documents)
            progress.update(task, completed=True)

        chunk_stats = text_splitter.get_chunk_statistics(chunks)
        console.print(f"[green]✓ Created {len(chunks)} chunks[/green]")
        console.print(f"[dim]Average chunk size: {chunk_stats['avg_chunk_size']:.0f} characters[/dim]")

        # Generate embeddings
        console.print("\n[yellow]Step 6: Generating embeddings...[/yellow]")
        console.print("[dim]This may take several minutes depending on the number of chunks...[/dim]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:

            # Calculate total batches
            total_batches = (len(chunks) + args.batch_size - 1) // args.batch_size
            task = progress.add_task(
                f"[cyan]Embedding {len(chunks)} chunks in {total_batches} batches...",
                total=len(chunks)
            )

            # Embed in batches with progress updates
            embedded_docs = []
            for i in range(0, len(chunks), args.batch_size):
                batch = chunks[i:i + args.batch_size]
                batch_embedded = embedding_service.embed_documents(
                    batch,
                    use_cache=not args.skip_cache,
                    show_progress=False
                )
                embedded_docs.extend(batch_embedded)
                progress.update(task, advance=len(batch))

        console.print(f"[green]✓ Generated {len(embedded_docs)} embeddings[/green]")

        # Show cache statistics
        cache_stats = embedding_service.get_embedding_stats()
        console.print(f"[dim]Cache: {cache_stats['cached_embeddings']} embeddings, {cache_stats['cache_size_mb']} MB[/dim]")

        # Insert into Milvus
        console.print("\n[yellow]Step 7: Inserting into Milvus...[/yellow]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:

            task = progress.add_task(
                "[cyan]Inserting documents...",
                total=len(embedded_docs)
            )

            # Insert in batches
            insert_batch_size = 100
            all_ids = []
            for i in range(0, len(embedded_docs), insert_batch_size):
                batch = embedded_docs[i:i + insert_batch_size]
                ids = vector_store.insert_documents(batch, batch_size=insert_batch_size)
                all_ids.extend(ids)
                progress.update(task, advance=len(batch))

        console.print(f"[green]✓ Inserted {len(all_ids)} documents[/green]")

        # Load collection for querying
        console.print("\n[yellow]Step 8: Loading collection into memory...[/yellow]")
        vector_store.load_collection()
        console.print("[green]✓ Collection loaded and ready for search[/green]")

        # Get final statistics
        collection_stats = vector_store.get_collection_stats()

        # Calculate total time
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)

        # Display final summary
        console.print("\n[bold green]Ingestion Complete![/bold green]\n")

        summary_table = Table(show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("PDF Files Processed", str(len(pdf_counts)))
        summary_table.add_row("Total Pages", str(len(all_documents)))
        summary_table.add_row("Total Chunks", str(len(chunks)))
        summary_table.add_row("Documents in Milvus", str(collection_stats['num_entities']))
        summary_table.add_row("Avg Chunk Size", f"{chunk_stats['avg_chunk_size']:.0f} chars")
        summary_table.add_row("Embedding Dimension", str(cache_stats['dimension']))
        summary_table.add_row("Processing Time", f"{minutes}m {seconds}s")

        console.print(summary_table)

        # Test search
        console.print("\n[yellow]Running test search...[/yellow]")
        test_query = "What are the meanings of the 12 astrological houses?"
        console.print(f"[dim]Query: {test_query}[/dim]\n")

        query_embedding = embedding_service.embed_text(test_query)
        test_results = vector_store.search(query_embedding, top_k=3)

        if test_results:
            console.print("[green]✓ Test search successful![/green]")
            console.print(f"[dim]Found {len(test_results)} relevant results:[/dim]\n")

            for i, result in enumerate(test_results, 1):
                console.print(
                    f"  {i}. [cyan]{result['source_file']}[/cyan] "
                    f"(Page {result['page_number']}) - Score: {result['score']:.4f}"
                )
        else:
            console.print("[yellow]⚠ No results found in test search[/yellow]")

        console.print("\n[bold cyan]Knowledge base is ready for use![/bold cyan]\n")

        # Disconnect
        vector_store.disconnect()

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Ingestion interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
