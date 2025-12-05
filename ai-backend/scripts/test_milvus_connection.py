#!/usr/bin/env python3
"""
Test script to verify Milvus connection and basic operations
"""
from pymilvus import connections, utility
import sys
from rich.console import Console
from rich.table import Table

console = Console()

def test_milvus_connection():
    """Test connection to Milvus server"""
    try:
        console.print("\n[bold blue]Testing Milvus Connection...[/bold blue]\n")

        # Connect to Milvus
        console.print("[yellow]Connecting to Milvus at localhost:19531...[/yellow]")
        connections.connect(
            alias="default",
            host="localhost",
            port="19531"
        )
        console.print("[green]✓ Successfully connected to Milvus![/green]\n")

        # Get server version
        version = utility.get_server_version()
        console.print(f"[cyan]Milvus Server Version:[/cyan] {version}\n")

        # List all collections
        console.print("[yellow]Listing existing collections...[/yellow]")
        collections = utility.list_collections()

        if collections:
            table = Table(title="Existing Collections")
            table.add_column("Collection Name", style="cyan")
            for col in collections:
                table.add_row(col)
            console.print(table)
        else:
            console.print("[dim]No collections found (this is normal for a fresh installation)[/dim]\n")

        # Disconnect
        connections.disconnect("default")
        console.print("\n[green]✓ All tests passed! Milvus is ready to use.[/green]\n")

        return True

    except Exception as e:
        console.print(f"\n[bold red]✗ Connection failed:[/bold red] {str(e)}\n")
        console.print("[yellow]Troubleshooting steps:[/yellow]")
        console.print("1. Check if Docker containers are running: docker-compose ps")
        console.print("2. Check Milvus logs: docker logs milvus-standalone")
        console.print("3. Ensure port 19530 is not blocked by firewall\n")
        return False

if __name__ == "__main__":
    success = test_milvus_connection()
    sys.exit(0 if success else 1)
