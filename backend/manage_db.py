#!/usr/bin/env python3
"""
Database management CLI for AegisCare
"""

from app.db.connection import init_database, get_conn
import typer
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


app = typer.Typer()


@app.command()
def init():
    """Initialize database and create all tables"""
    typer.echo("🚀 Initializing AegisCare database...")
    try:
        init_database()
        typer.echo("✅ Database initialized successfully!")
    except Exception as e:
        typer.echo(f"❌ Failed to initialize database: {e}")
        raise typer.Exit(1)


@app.command()
def status():
    """Check database connection status"""
    typer.echo("🔍 Checking database connection...")
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION() as version")
            result = cur.fetchone()
            typer.echo(f"✅ Connected to MySQL {result['version']}")

            # Check tables
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
            if tables:
                typer.echo(f"📊 Found {len(tables)} tables:")
                for table in tables:
                    table_name = list(table.values())[0]
                    typer.echo(f"   - {table_name}")
            else:
                typer.echo("📊 No tables found")

        conn.close()
    except Exception as e:
        typer.echo(f"❌ Database connection failed: {e}")
        raise typer.Exit(1)


@app.command()
def reset():
    """Reset database (drop all tables and recreate)"""
    if not typer.confirm("⚠️  This will delete all data. Are you sure?"):
        typer.echo("Operation cancelled")
        return

    typer.echo("🗑️  Resetting database...")
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            # Drop all tables
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()

            for table in tables:
                table_name = list(table.values())[0]
                cur.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                typer.echo(f"   Dropped table: {table_name}")

            cur.execute("SET FOREIGN_KEY_CHECKS = 1")
            conn.commit()

        conn.close()

        # Reinitialize
        init_database()
        typer.echo("✅ Database reset successfully!")

    except Exception as e:
        typer.echo(f"❌ Failed to reset database: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
