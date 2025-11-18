"""VM instance management commands"""

import httpx
import typer
from rich.console import Console
from rich.table import Table

from ...shared.config import config

console = Console()

vms_app = typer.Typer(name="vms", help="VM instance management commands")


@vms_app.command("start-instance")
def start_instance(
    hardware_profile: str = typer.Option(
        "a100", "--hardware-profile", "-h", help="Hardware profile (cpu, a100, h100, etc.)"
    ),
    public_key: str = typer.Option(..., "--key", "-k", help="SSH public key for VM access"),
    name: str | None = typer.Option(None, "--name", "-n", help="Friendly name for the instance"),
    cpu: int | None = typer.Option(None, "--cpu", help="Number of CPU cores (uses hardware profile default if not specified)"),
    memory: int | None = typer.Option(None, "--memory", help="Memory in GB (uses hardware profile default if not specified)"),
    disk: int | None = typer.Option(None, "--disk", help="Disk size in GB (uses hardware profile default if not specified)"),
    gpu_count: int | None = typer.Option(None, "--gpu-count", help="Number of GPUs (uses hardware profile default if not specified)"),
):
    """Start a new VM instance"""
    try:
        # Ensure we have a valid token
        config.get_client()

        # Create instance specs - only include values that were explicitly provided
        instance_specs = {}
        if cpu is not None:
            instance_specs["cpu"] = cpu
        if memory is not None:
            instance_specs["memory"] = memory
        if disk is not None:
            instance_specs["disk"] = disk
        if gpu_count is not None:
            instance_specs["gpu_count"] = gpu_count

        # Create request payload
        payload = {
            "instance_specs": instance_specs,
            "user_public_key": public_key,
            "hardware_profile": hardware_profile,
        }

        if name:
            payload["name"] = name

        # Make API request
        console.print("[dim]Creating VM instance...[/dim]")
        response = httpx.post(
            f"{config.base_url}/api/v2/external/vms/create",
            headers={"Authorization": f"Bearer {config.api_key}"},
            json=payload,
            timeout=60.0,
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            try:
                error_data = response.json()
                console.print(f"[red]{error_data.get('detail', response.text)}[/red]")
            except Exception:
                console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()

        console.print("[green]✅ VM instance created successfully![/green]")
        console.print(f"[bold]VM ID:[/bold] {data['vm_id']}")
        console.print(f"[bold]Status:[/bold] {data['status']}")
        if data.get("ip_address"):
            console.print(f"[bold]IP Address:[/bold] {data['ip_address']}")
        if data.get("name"):
            console.print(f"[bold]Name:[/bold] {data['name']}")
        console.print(f"[dim]Created at: {data['created_at']}[/dim]")

        if data.get("ip_address"):
            console.print(f"\n[cyan]SSH command:[/cyan] ssh -i <your-key> ubuntu@{data['ip_address']}")

    except httpx.TimeoutException:
        console.print("[red]Error: Request timed out[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@vms_app.command("list-instances")
def list_instances():
    """List all VM instances"""
    try:
        # Ensure we have a valid token
        config.get_client()

        # Make API request
        response = httpx.get(
            f"{config.base_url}/api/v2/external/vms/list",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()
        vms = data.get("vms", [])

        if not vms:
            console.print("[yellow]No VM instances found.[/yellow]")
            return

        # Create table
        table = Table(title="VM Instances")
        table.add_column("VM ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("IP Address", style="blue")
        table.add_column("Hardware", style="magenta")
        table.add_column("Billed ($)", style="red")
        table.add_column("Created At", style="dim")

        for vm in vms:
            table.add_row(
                vm["vm_id"],
                vm.get("name", "-"),
                vm["status"],
                vm.get("ip_address", "-"),
                vm.get("hardware_profile", "-"),
                f"{vm.get('billed', 0):.4f}" if vm.get("billed") is not None else "-",
                vm["created_at"],
            )

        console.print(table)

    except httpx.TimeoutException:
        console.print("[red]Error: Request timed out[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@vms_app.command("instance-status")
def instance_status(
    vm_id: str = typer.Argument(..., help="VM instance ID"),
):
    """Get detailed status of a VM instance"""
    try:
        # Ensure we have a valid token
        config.get_client()

        # Make API request
        response = httpx.get(
            f"{config.base_url}/api/v2/external/vms/status/{vm_id}",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            try:
                error_data = response.json()
                console.print(f"[red]{error_data.get('detail', response.text)}[/red]")
            except Exception:
                console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()

        console.print(f"[bold cyan]VM Instance: {vm_id}[/bold cyan]\n")
        console.print(f"[bold]Status:[/bold] {data['status']}")
        if data.get("name"):
            console.print(f"[bold]Name:[/bold] {data['name']}")
        if data.get("ip_address"):
            console.print(f"[bold]IP Address:[/bold] {data['ip_address']}")
        console.print(f"[bold]Hardware Profile:[/bold] {data.get('hardware_profile', '-')}")
        if data.get("billed") is not None:
            console.print(f"[bold]Total Billed:[/bold] ${data['billed']:.4f}")
        if data.get("uptime_seconds") is not None:
            hours = data["uptime_seconds"] / 3600
            console.print(f"[bold]Uptime:[/bold] {hours:.2f} hours")
        console.print(f"[dim]Created at: {data['created_at']}[/dim]")

        if data.get("instance_specs"):
            console.print("\n[bold]Instance Specs:[/bold]")
            specs = data["instance_specs"]
            console.print(f"  CPU: {specs.get('cpu', '-')} cores")
            console.print(f"  Memory: {specs.get('memory', '-')} GB")
            console.print(f"  Disk: {specs.get('disk', '-')} GB")
            console.print(f"  GPU Count: {specs.get('gpu_count', '-')}")

        if data.get("ip_address"):
            console.print(f"\n[cyan]SSH command:[/cyan] ssh -i <your-key> ubuntu@{data['ip_address']}")

    except httpx.TimeoutException:
        console.print("[red]Error: Request timed out[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@vms_app.command("terminate-instance")
def terminate_instance(
    vm_id: str = typer.Argument(..., help="VM instance ID to terminate"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Terminate (delete) a VM instance"""
    try:
        # Ensure we have a valid token
        config.get_client()

        # Confirm termination unless --force is used
        if not force:
            confirm = typer.confirm(f"Are you sure you want to terminate VM {vm_id}?")
            if not confirm:
                console.print("[yellow]Termination cancelled.[/yellow]")
                return

        # Make API request
        console.print("[dim]Terminating VM instance...[/dim]")
        response = httpx.delete(
            f"{config.base_url}/api/v2/external/vms/delete/{vm_id}",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=30.0,
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            try:
                error_data = response.json()
                console.print(f"[red]{error_data.get('detail', response.text)}[/red]")
            except Exception:
                console.print(f"[red]{response.text}[/red]")
            raise typer.Exit(1)

        data = response.json()

        console.print(f"[green]✅ {data.get('message', 'VM instance terminated successfully')}[/green]")

    except httpx.TimeoutException:
        console.print("[red]Error: Request timed out[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
