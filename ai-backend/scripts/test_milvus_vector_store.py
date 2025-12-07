#!/usr/bin/env python3
# Test script for Milvus vector store service

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.knowledge_base.vector_store import get_vector_store
from app.rag.knowledge_base.pdf_loader import get_pdf_loader
from app.rag.knowledge_base.text_splitter import get_text_splitter
from app.rag.embeddings.service import get_embedding_service
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


def main():
    console = Console()

    console.print("\n[bold cyan]Milvus Vector Store Test[/bold cyan]\n")

    try:
        # Initialize services
        console.print("[yellow]Initializing services...[/yellow]")
        vector_store = get_vector_store()
        pdf_loader = get_pdf_loader()
        text_splitter = get_text_splitter(chunk_size=1024, chunk_overlap=200)
        embedding_service = get_embedding_service(batch_size=10)

        # Test 1: Connect to Milvus
        console.print("\n[bold cyan]Test 1: Milvus Connection[/bold cyan]\n")
        console.print("[yellow]Connecting to Milvus...[/yellow]")
        vector_store.connect()
        console.print("[green]✓ Successfully connected to Milvus[/green]")

        # Test 2: Create collection
        console.print("\n[bold cyan]Test 2: Create Collection[/bold cyan]\n")
        console.print("[yellow]Creating collection...[/yellow]")
        vector_store.create_collection(drop_existing=True)
        console.print(f"[green]✓ Collection '{vector_store.collection_name}' created[/green]")

        # Test 3: Create index
        console.print("\n[bold cyan]Test 3: Create Index[/bold cyan]\n")
        console.print("[yellow]Creating index on embedding field...[/yellow]")
        vector_store.create_index()
        console.print("[green]✓ Index created successfully[/green]")

        # Test 4: Insert sample documents
        console.print("\n[bold cyan]Test 4: Insert Sample Documents[/bold cyan]\n")

        # Load a small sample of documents
        console.print("[yellow]Loading sample PDF (first 3 pages)...[/yellow]")
        pdf_files = pdf_loader.get_pdf_files()

        if not pdf_files:
            console.print("[red]No PDF files found![/red]")
            return

        documents = pdf_loader.load_single_pdf(pdf_files[0])
        sample_docs = documents[:3]
        console.print(f"[cyan]Loaded {len(sample_docs)} pages from {pdf_files[0].name}[/cyan]")

        # Split into chunks
        console.print("[yellow]Splitting into chunks...[/yellow]")
        chunks = text_splitter.split_documents(sample_docs)
        console.print(f"[cyan]Created {len(chunks)} chunks[/cyan]")

        # Generate embeddings
        console.print("[yellow]Generating embeddings...[/yellow]")
        embedded_docs = embedding_service.embed_documents(chunks, show_progress=False)
        console.print(f"[green]✓ Generated {len(embedded_docs)} embeddings[/green]")

        # Insert into Milvus
        console.print("[yellow]Inserting into Milvus...[/yellow]")
        inserted_ids = vector_store.insert_documents(embedded_docs, batch_size=100)
        console.print(f"[green]✓ Inserted {len(inserted_ids)} documents[/green]")

        # Test 5: Load collection for search
        console.print("\n[bold cyan]Test 5: Load Collection[/bold cyan]\n")
        console.print("[yellow]Loading collection into memory...[/yellow]")
        vector_store.load_collection()
        console.print("[green]✓ Collection loaded[/green]")

        # Test 6: Search
        console.print("\n[bold cyan]Test 6: Similarity Search[/bold cyan]\n")

        query_text = "What does the first house represent in astrology?"
        console.print(f"[yellow]Query:[/yellow] {query_text}")

        console.print("[yellow]Generating query embedding...[/yellow]")
        query_embedding = embedding_service.embed_text(query_text)

        console.print("[yellow]Searching for similar documents...[/yellow]")
        search_results = vector_store.search(
            query_embedding=query_embedding,
            top_k=3
        )

        console.print(f"[green]✓ Found {len(search_results)} results[/green]\n")

        # Display results
        for i, result in enumerate(search_results, 1):
            panel_content = f"""[cyan]Score:[/cyan] {result['score']:.4f}
[cyan]Distance:[/cyan] {result['distance']:.4f}
[cyan]Source:[/cyan] {result['source_file']}
[cyan]Page:[/cyan] {result['page_number']}
[cyan]Category:[/cyan] {result['category']}

[yellow]Text Preview:[/yellow]
{result['text'][:200]}..."""

            console.print(Panel(
                panel_content,
                title=f"[bold]Result {i}[/bold]",
                border_style="blue"
            ))

        # Test 7: Filtered search
        console.print("\n[bold cyan]Test 7: Filtered Search[/bold cyan]\n")

        category = embedded_docs[0]['metadata'].get('category')
        console.print(f"[yellow]Searching in category:[/yellow] {category}")

        filtered_results = vector_store.search_with_filters(
            query_embedding=query_embedding,
            top_k=2,
            category=category
        )

        console.print(f"[green]✓ Found {len(filtered_results)} results in category '{category}'[/green]")

        # Test 8: Collection statistics
        console.print("\n[bold cyan]Test 8: Collection Statistics[/bold cyan]\n")

        stats = vector_store.get_collection_stats()

        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats_table.add_row("Collection Name", stats['name'])
        stats_table.add_row("Total Entities", str(stats['num_entities']))
        stats_table.add_row("Number of Indexes", str(len(stats['indexes'])))

        console.print(stats_table)

        # Cleanup
        console.print("\n[yellow]Test completed. Collection remains for further use.[/yellow]")
        console.print("[dim]To drop the collection, uncomment the cleanup code.[/dim]")

        # Uncomment to drop collection after test
        # console.print("\n[yellow]Cleaning up...[/yellow]")
        # vector_store.drop_collection()
        # console.print("[green]✓ Collection dropped[/green]")

        # Disconnect
        vector_store.disconnect()

        console.print("\n[bold green]✓ All Milvus Vector Store Tests Completed Successfully![/bold green]\n")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
