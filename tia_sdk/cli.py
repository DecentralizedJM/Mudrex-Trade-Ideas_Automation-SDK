"""
CLI interface for Mudrex Signal Automator SDK.
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
        from .constants import BROADCASTER_URL
        
        console.print("[bold]Mudrex API Credentials[/bold]")
        console.print("[dim]Get these from Mudrex Settings → API Management[/dim]")
        console.print("[dim]Required permissions: Futures Trading[/dim]\n")
        console.print("[yellow]⚠️  Important:[/yellow]")
        console.print("   • Your API Secret is a long string (usually 40+ characters)")
        console.print("   • Copy the ENTIRE secret - don't miss any characters")
        console.print("   • Make sure 'Futures Trading' permission is enabled")
        console.print("   • The secret will be validated immediately\n")
        
        # Prompt for Mudrex credentials with validation
        while True:
            mudrex_api_secret = click.prompt("🔑 Mudrex API Secret", type=str, hide_input=True)
            
            # Basic format validation
            if not mudrex_api_secret or len(mudrex_api_secret.strip()) < 10:
                console.print("[red]❌ API Secret appears too short. Please check and try again.[/red]")
                console.print("[dim]API Secrets are typically 40+ characters long[/dim]\n")
                if not click.confirm("Try again?", default=True):
                    console.print("[yellow]Setup cancelled[/yellow]")
                    sys.exit(0)
                continue
            
            # Check for common mistakes
            if mudrex_api_secret.strip() in ["your_mudrex_api_secret", "your-secret", "api_secret", ""]:
                console.print("[red]❌ Please enter your actual API Secret, not a placeholder[/red]\n")
                if not click.confirm("Try again?", default=True):
                    console.print("[yellow]Setup cancelled[/yellow]")
                    sys.exit(0)
                continue
            
            break
        
        # Validate credentials immediately
        console.print("\n[dim]Validating credentials...[/dim]")
        
        async def validate_creds():
            try:
                from mudrex import MudrexClient
                client = MudrexClient(api_secret=mudrex_api_secret)
                balance = await asyncio.to_thread(client.wallet.get_futures_balance)
                return True, float(balance.available)  # mudrex library uses .available
            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg or "Unauthorized" in error_msg.lower():
                    return False, "Invalid API Secret - Please check your API Secret from Mudrex Settings"
                elif "403" in error_msg or "Forbidden" in error_msg.lower():
                    return False, "API Secret missing 'Futures Trading' permission - Enable it in Mudrex Settings"
                elif "aut" in error_msg.lower() or "auth" in error_msg.lower():
                    return False, "Invalid API Secret - Please enter your correct API Secret"
                else:
                    # Try to extract meaningful error message
                    if "connection" in error_msg.lower() or "network" in error_msg.lower():
                        return False, "Connection error - Check your internet connection"
                    elif "timeout" in error_msg.lower():
                        return False, "Connection timeout - Please try again"
                    else:
                        return False, f"Unable to validate API Secret - {error_msg[:100]}"
        
        valid, result = asyncio.run(validate_creds())
        
        if not valid:
            console.print(f"\n[red]❌ {result}[/red]")
            console.print("\n[bold]What to do:[/bold]")
            if "Invalid API Secret" in result:
                console.print("• Go to Mudrex → Settings → API Management")
                console.print("• Copy your API Secret (the entire long string)")
                console.print("• Make sure you copied all characters - no missing parts")
                console.print("• Run 'signal-sdk setup' again with the correct secret")
            elif "Futures Trading" in result:
                console.print("• Go to Mudrex → Settings → API Management")
                console.print("• Click on your API key to edit it")
                console.print("• Enable 'Futures Trading' permission")
                console.print("• Save and try again")
            else:
                console.print("• Check your internet connection")
                console.print("• Verify your API Secret is correct")
                console.print("• Try again in a few moments")
            console.print("\n[yellow]Need help? Run 'signal-sdk doctor' for detailed diagnostics[/yellow]")
            sys.exit(1)
        
        console.print(f"[green]✅ Credentials valid! Balance: {result:.2f} USDT[/green]")
        
        console.print("\n[bold]Trading Parameters[/bold]")
        console.print("[dim]Minimum trade amount: 5.0 USDT (Mudrex requirement)[/dim]\n")
        trade_amount = click.prompt("💰 Trade Amount per Signal (USDT)", type=float, default=5.0)
        
        # Validate minimum
        if trade_amount < 5.0:
            console.print("[yellow]⚠️  Trade amount below minimum (5.0 USDT). Setting to 5.0 USDT[/yellow]")
            trade_amount = 5.0
        
        max_leverage = click.prompt("⚡ Maximum Leverage", type=int, default=25)
        
        # Broadcaster URL configuration
        console.print("\n[bold]Broadcaster Connection[/bold]")
        console.print("[dim]WebSocket URL where signals are broadcast from[/dim]")
        console.print(f"[dim]Default: {BROADCASTER_URL}[/dim]\n")
        broadcaster_url = click.prompt(
            "🌐 Broadcaster WebSocket URL",
            type=str,
            default=BROADCASTER_URL,
            show_default=False
        )
        
        # Validate URL format
        if not broadcaster_url.startswith(("ws://", "wss://")):
            console.print("[yellow]⚠️  URL should start with ws:// or wss://[/yellow]")
            console.print("[yellow]   Using default URL instead[/yellow]")
            broadcaster_url = BROADCASTER_URL
        
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
                "url": broadcaster_url,
                "client_id": client_id,
                "telegram_id": telegram_id if telegram_id > 0 else None
            },
            "mudrex": {
                "api_secret": mudrex_api_secret
            },
            "trading": {
                "enabled": True,
                "trade_amount_usdt": trade_amount,
                "max_leverage": max_leverage,
                "min_order_value": 5.0,  # Mudrex minimum requirement
                "auto_execute": True
            },
            "risk": {
                "max_daily_trades": 999999,  # Disabled (no limit)
                "max_open_positions": 999999,  # Disabled (no limit)
                "stop_on_daily_loss": 0.0,  # Disabled
                "min_balance": 0.0  # Disabled (no minimum)
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
        
        # Test broadcaster connection
        console.print("\n[bold]Testing broadcaster connection...[/bold]")
        
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
            console.print("[green]✅ Broadcaster connection successful![/green]")
        else:
            console.print("[yellow]⚠️  Could not connect to broadcaster[/yellow]")
            console.print("[dim]This may be normal if the service is starting up[/dim]")
        
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
        try:
            cfg = Config(config)
        except FileNotFoundError:
            console.print(f"[red]❌ Config file not found: {config}[/red]")
            console.print("\n[bold]Quick fix:[/bold]")
            console.print("  [cyan]signal-sdk setup[/cyan]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]❌ Config Error: {e}[/red]")
            console.print("\n[bold]Run setup to fix:[/bold]")
            console.print("  [cyan]signal-sdk setup[/cyan]")
            sys.exit(1)
        
        # Validate config
        is_valid, errors = cfg.validate()
        if not is_valid:
            console.print("[red]❌ Configuration errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            console.print("\n[bold]Run setup to fix:[/bold]")
            console.print("  [cyan]signal-sdk setup[/cyan]")
            sys.exit(1)
        
        # Setup logging
        setup_logging(cfg)
        
        console.print("[bold green]🚀 Mudrex Signal Automator v1.0.0[/bold green]")
        console.print(f"[dim]Connected as: {cfg.broadcaster.client_id}[/dim]\n")
        
        # Validate Mudrex credentials before starting
        console.print("[dim]Validating Mudrex credentials...[/dim]")
        
        try:
            executor = TradeExecutor(cfg)
            
            async def validate_api():
                return await executor.validate_credentials()
            
            valid, msg = asyncio.run(validate_api())
            
            if not valid:
                console.print(f"[red]❌ Mudrex API Error: {msg}[/red]")
                console.print("\n[bold]Run 'signal-sdk doctor' to diagnose[/bold]")
                sys.exit(1)
            
            console.print(f"[green]✅ Mudrex API: {msg}[/green]\n")
        
        except Exception as e:
            console.print(f"[red]❌ Failed to initialize: {e}[/red]")
            sys.exit(1)
        
        # Create client
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
def doctor(config):
    """Diagnose connectivity and configuration issues."""
    console.print("[bold]🩺 Signal SDK Doctor[/bold]\n")
    
    all_ok = True
    
    # Check 1: Config file exists
    console.print("[bold]1. Configuration File[/bold]")
    if Path(config).exists():
        console.print(f"   [green]✅ Found: {config}[/green]")
    else:
        console.print(f"   [red]❌ Not found: {config}[/red]")
        console.print("   [dim]Run 'signal-sdk setup' to create one[/dim]")
        sys.exit(1)
    
    # Load config
    try:
        cfg = Config(config)
        console.print("   [green]✅ Config loaded successfully[/green]")
    except Exception as e:
        console.print(f"   [red]❌ Failed to load config: {e}[/red]")
        sys.exit(1)
    
    # Check 2: Config validation
    console.print("\n[bold]2. Configuration Validation[/bold]")
    is_valid, errors = cfg.validate()
    if is_valid:
        console.print("   [green]✅ All required fields present[/green]")
    else:
        all_ok = False
        console.print("   [red]❌ Configuration errors:[/red]")
        for error in errors:
            console.print(f"      • {error}")
    
    # Check 3: Broadcaster connection
    console.print("\n[bold]3. Broadcaster Connection[/bold]")
    console.print(f"   [dim]URL: {cfg.broadcaster.url}[/dim]")
    
    # Check if URL is placeholder
    if "your-broadcaster" in cfg.broadcaster.url or "example" in cfg.broadcaster.url.lower():
        all_ok = False
        console.print("   [yellow]⚠️  Placeholder URL detected[/yellow]")
        console.print("   [dim]Please update config.toml with your actual broadcaster URL[/dim]")
        console.print("   [dim]Example: wss://your-broadcaster.railway.app/ws[/dim]")
    else:
        async def test_broadcaster():
            try:
                client = SignalClient(cfg)
                connected = await client.connect()
                if connected:
                    await client.disconnect()
                    return True, "Connected successfully"
                return False, "Connection failed"
            except Exception as e:
                return False, str(e)
        
        try:
            success, msg = asyncio.run(test_broadcaster())
            if success:
                console.print(f"   [green]✅ {msg}[/green]")
            else:
                all_ok = False
                console.print(f"   [red]❌ {msg}[/red]")
                console.print("   [dim]Troubleshooting:[/dim]")
                console.print("   • Check your internet connection")
                console.print("   • Verify the broadcaster URL is correct")
                console.print("   • The service may be temporarily down")
        except Exception as e:
            all_ok = False
            error_msg = str(e)
            console.print(f"   [red]❌ Error: {error_msg}[/red]")
            if "Name or service not known" in error_msg or "Failed to resolve" in error_msg:
                console.print("   [dim]Troubleshooting:[/dim]")
                console.print("   • Check if the broadcaster URL is correct")
                console.print("   • Ensure the broadcaster service is running")
    
    # Check 4: Mudrex API
    console.print("\n[bold]4. Mudrex API[/bold]")
    
    if not cfg.mudrex.api_secret:
        all_ok = False
        console.print("   [red]❌ API Secret not configured[/red]")
    else:
        console.print("   [dim]Testing API credentials...[/dim]")
        
        async def test_mudrex():
            try:
                executor = TradeExecutor(cfg)
                return await executor.validate_credentials()
            except Exception as e:
                return False, str(e)
        
        try:
            success, msg = asyncio.run(test_mudrex())
            if success:
                console.print(f"   [green]✅ {msg}[/green]")
            else:
                all_ok = False
                console.print(f"   [red]❌ {msg}[/red]")
                
                # Provide specific troubleshooting
                if "Invalid API Secret" in msg:
                    console.print("\n   [bold]What to do:[/bold]")
                    console.print("   • Go to Mudrex → Settings → API Management")
                    console.print("   • Copy your API Secret (the entire long string)")
                    console.print("   • Update config.toml with the correct secret")
                    console.print("   • Make sure you copied all characters")
                elif "Futures Trading" in msg:
                    console.print("\n   [bold]What to do:[/bold]")
                    console.print("   • Go to Mudrex → Settings → API Management")
                    console.print("   • Click on your API key to edit it")
                    console.print("   • Enable 'Futures Trading' permission")
                    console.print("   • Save and try again")
                elif "temporarily unavailable" in msg or "Connection" in msg:
                    console.print("\n   [bold]What to do:[/bold]")
                    console.print("   • Check your internet connection")
                    console.print("   • Wait a few minutes and try again")
                    console.print("   • The Mudrex service may be temporarily down")
        except Exception as e:
            all_ok = False
            console.print(f"   [red]❌ Error: {e}[/red]")
    
    # Summary
    console.print("\n" + "=" * 40)
    if all_ok:
        console.print("[bold green]✅ All checks passed![/bold green]")
        console.print("\n[dim]You're ready to start:[/dim]")
        console.print("  [cyan]signal-sdk start[/cyan]")
    else:
        console.print("[bold red]❌ Some checks failed[/bold red]")
        console.print("\n[dim]Fix the issues above and run doctor again[/dim]")
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
        console.print("[dim]Run 'signal-sdk setup' to create one[/dim]")
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
