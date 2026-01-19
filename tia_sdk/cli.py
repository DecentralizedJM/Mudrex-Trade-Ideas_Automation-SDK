"""
CLI interface for TIA Signal Automator SDK.
"""

import click
import asyncio
import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from .config import Config
from .client import SignalClient
from .executor import TradeExecutor

console = Console()


def setup_logging(config: Config):
    """Setup logging configuration."""
    log_level = getattr(logging, config.logging.level.upper())
    
    handlers = []
    
    # Console handler
    if config.logging.console:
        handlers.append(RichHandler(
            rich_tracebacks=True,
            console=console,
            show_time=True,
            show_path=False
        ))
    
    # File handler
    if config.logging.file:
        if config.logging.rotate:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                config.logging.file,
                maxBytes=config.logging.max_bytes,
                backupCount=config.logging.backup_count
            )
        else:
            file_handler = logging.FileHandler(config.logging.file)
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        ))
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        handlers=handlers
    )


@click.group()
@click.version_option(version="1.0.0")
def main():
    """Mudrex Signal Automator - Receive and execute live trading signals."""
    pass


@main.command()
@click.option('--output', '-o', default='config.toml', help='Output config file path')
def init(output):
    """Generate configuration file (advanced users)."""
    try:
        if Path(output).exists():
            if not click.confirm(f'{output} already exists. Overwrite?'):
                console.print("[yellow]Cancelled[/yellow]")
                return
        
        Config.generate_example(output)
        console.print(f"[green]✅ Config generated: {output}[/green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"1. Edit {output} with your credentials")
        console.print("2. Run: signal-sdk start")
        console.print("\n[dim]Tip: Use 'signal-sdk setup' for interactive configuration[/dim]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--output', '-o', default='config.toml', help='Config file path')
def setup(output):
    """Interactive setup - easiest way to get started!"""
    try:
        console.print("[bold green]🚀 Mudrex Signal Automator - Setup[/bold green]\n")
        
        # Check if config exists
        if Path(output).exists():
            if not click.confirm(f'{output} already exists. Overwrite?'):
                console.print("[yellow]Setup cancelled[/yellow]")
                return
        
        # Import constants for broadcaster config
        from .constants import BROADCASTER_URL, BROADCASTER_API_SECRET
        
        console.print("[bold]Mudrex API Credentials[/bold]")
        console.print("[dim]Get these from Mudrex Settings → API Management[/dim]\n")
        
        # Prompt for Mudrex credentials
        mudrex_api_key = click.prompt("🔑 Mudrex API Key", type=str)
        mudrex_api_secret = click.prompt("🔑 Mudrex API Secret", type=str, hide_input=True)
        
        console.print("\n[bold]Trading Parameters[/bold]")
        trade_amount = click.prompt("💰 Trade Amount per Signal (USDT)", type=float, default=50.0)
        max_leverage = click.prompt("⚡ Maximum Leverage", type=int, default=10)
        
        # Optional: Telegram ID for notifications
        console.print("\n[bold]Optional Settings[/bold]")
        telegram_id = click.prompt("📱 Telegram ID (for notifications, optional)", type=int, default=0)
        
        # Generate client ID
        import uuid
        client_id = f"sdk-{uuid.uuid4().hex[:8]}"
        
        # Create config
        import toml
        config_data = {
            "broadcaster": {
                "url": BROADCASTER_URL,
                "api_secret": BROADCASTER_API_SECRET,
                "client_id": client_id,
                "telegram_id": telegram_id if telegram_id > 0 else None
            },
            "mudrex": {
                "api_key": mudrex_api_key,
                "api_secret": mudrex_api_secret
            },
            "trading": {
                "enabled": True,
                "trade_amount_usdt": trade_amount,
                "max_leverage": max_leverage,
                "min_order_value": 8.0,
                "auto_execute": True
            },
            "risk": {
                "max_daily_trades": 20,
                "max_open_positions": 5,
                "stop_on_daily_loss": 1000.0,
                "min_balance": 100.0
            },
            "logging": {
                "level": "INFO",
                "file": "signal_sdk.log",
                "console": True,
                "rotate": True,
                "max_bytes": 10485760,
                "backup_count": 5
            }
        }
        
        # Save config
        with open(output, 'w') as f:
            toml.dump(config_data, f)
        
        console.print(f"\n[green]✅ Configuration saved to {output}[/green]")
        
        # Test connection
        console.print("\n[bold]Testing connection...[/bold]")
        
        async def test_conn():
            try:
                cfg = Config(output)
                from .client import SignalClient
                client = SignalClient(cfg)
                
                connected = await client.connect()
                if connected:
                    await client.disconnect()
                    return True
                return False
            except:
                return False
        
        if asyncio.run(test_conn()):
            console.print("[green]✅ Connection successful![/green]")
        else:
            console.print("[yellow]⚠️  Could not connect to signal provider[/yellow]")
            console.print("[dim]This is normal if the service is not running yet[/dim]")
        
        console.print("\n[bold green]🎉 Setup complete![/bold green]")
        console.print("\n[bold]Next step:[/bold]")
        console.print("  [cyan]signal-sdk start[/cyan]")
        console.print("\n[dim]Your configuration is saved in config.toml[/dim]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled[/yellow]")
        sys.exit(0)
    
    except Exception as e:
        console.print(f"\n[red]❌ Setup failed: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--config', '-c', default='config.toml', help='Config file path')
def start(config):
    """Start receiving and executing signals."""
    try:
        # Load config
        cfg = Config(config)
        
        # Validate config
        is_valid, errors = cfg.validate()
        if not is_valid:
            console.print("[red]❌ Configuration errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            sys.exit(1)
        
        # Setup logging
        setup_logging(cfg)
        
        console.print("[bold green]🚀 Mudrex Signal Automator v1.0.0[/bold green]")
        console.print(f"[dim]Connected as: {cfg.broadcaster.client_id}[/dim]\n")
        
        # Create components
        executor = TradeExecutor(cfg)
        client = SignalClient(cfg)
        
        # Setup callbacks
        async def on_connected():
            console.print("[green]✅ Connected to broadcaster[/green]")
        
        async def on_disconnected():
            console.print("[yellow]⚠️  Disconnected from broadcaster[/yellow]")
        
        async def on_signal(signal):
            console.print(f"[cyan]📡 Signal: {signal.signal_type.value} {signal.symbol}[/cyan]")
            result = await executor.execute_signal(signal)
            if result.success:
                console.print(f"[green]✅ Executed: {result.message}[/green]")
            else:
                console.print(f"[red]❌ Failed: {result.message}[/red]")
        
        async def on_close(close):
            console.print(f"[yellow]🔒 Close: {close.symbol} ({close.percentage}%)[/yellow]")
            result = await executor.close_position(close)
            if result.success:
                console.print(f"[green]✅ {result.message}[/green]")
            else:
                console.print(f"[red]❌ {result.message}[/red]")
        
        async def on_edit_sltp(edit):
            console.print(f"[blue]✏️  Edit SL/TP: {edit.symbol}[/blue]")
            result = await executor.update_sl_tp(edit)
            if result.success:
                console.print(f"[green]✅ {result.message}[/green]")
            else:
                console.print(f"[red]❌ {result.message}[/red]")
        
        async def on_leverage(lev):
            console.print(f"[magenta]⚡ Leverage: {lev.symbol} → {lev.leverage}x[/magenta]")
            result = await executor.update_leverage(lev)
            if result.success:
                console.print(f"[green]✅ {result.message}[/green]")
            else:
                console.print(f"[red]❌ {result.message}[/red]")
        
        client.on_connected = on_connected
        client.on_disconnected = on_disconnected
        client.on_signal = on_signal
        client.on_close = on_close
        client.on_edit_sltp = on_edit_sltp
        client.on_leverage = on_leverage
        
        # Run client
        console.print("[dim]Connecting to broadcaster...[/dim]\n")
        asyncio.run(client.start())
    
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Shutdown requested[/yellow]")
        sys.exit(0)
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        logging.exception("Fatal error")
        sys.exit(1)


@main.command()
@click.option('--config', '-c', default='config.toml', help='Config file path')
def status(config):
    """Check SDK configuration and connection status."""
    try:
        cfg = Config(config)
        
        # Display config summary
        table = Table(title="SDK Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Broadcaster URL", cfg.broadcaster.url)
        table.add_row("Client ID", cfg.broadcaster.client_id)
        table.add_row("Telegram ID", str(cfg.broadcaster.telegram_id) if cfg.broadcaster.telegram_id else "Not set")
        table.add_row("Trade Amount", f"{cfg.trading.trade_amount_usdt} USDT")
        table.add_row("Max Leverage", f"{cfg.trading.max_leverage}x")
        table.add_row("Auto Execute", "✅ Enabled" if cfg.trading.auto_execute else "❌ Disabled")
        table.add_row("Trading", "✅ Enabled" if cfg.trading.enabled else "❌ Disabled")
        
        console.print(table)
        
        # Validate
        is_valid, errors = cfg.validate()
        if is_valid:
            console.print("\n[green]✅ Configuration is valid[/green]")
        else:
            console.print("\n[red]❌ Configuration errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
    
    except FileNotFoundError:
        console.print(f"[red]❌ Config file not found: {config}[/red]")
        console.print("[dim]Run 'signal-sdk init' to create one[/dim]")
        sys.exit(1)
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--config', '-c', default='config.toml', help='Config file path')
def test(config):
    """Test connection to broadcaster."""
    async def test_connection():
        try:
            cfg = Config(config)
            client = SignalClient(cfg)
            
            console.print("[dim]Testing connection...[/dim]\n")
            
            connected = await client.connect()
            
            if connected:
                console.print("[green]✅ Connection successful![/green]")
                await client.disconnect()
                return True
            else:
                console.print("[red]❌ Connection failed[/red]")
                return False
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            return False
    
    try:
        success = asyncio.run(test_connection())
        sys.exit(0 if success else 1)
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--limit', '-n', default=10, help='Number of recent trades')
def history(limit):
    """View trade history."""
    console.print("[yellow]Trade history feature coming soon![/yellow]")
    console.print("[dim]Will display recent trade executions and results[/dim]")


if __name__ == '__main__':
    main()
