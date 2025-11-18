"""Engine CLI commands for engines_studios system."""

import os
import subprocess
from typing import Optional

import click

from .api_client import StudioManagerClient
from .auth import get_aws_username
from .progress import format_idle_state, format_time_ago, wait_with_progress


def _update_ssh_config_silent(client: StudioManagerClient, env: str) -> bool:
    """Update SSH config silently. Returns True if successful."""
    ssh_config_path = os.path.expanduser("~/.ssh/config")

    try:
        # Read existing config
        if os.path.exists(ssh_config_path):
            with open(ssh_config_path, "r") as f:
                lines = f.readlines()
        else:
            lines = []

        # Remove managed entries
        managed_start = "# BEGIN DAYHOFF ENGINES\n"
        managed_end = "# END DAYHOFF ENGINES\n"

        new_lines = []
        skip = False
        for line in lines:
            if line == managed_start:
                skip = True
            elif line == managed_end:
                skip = False
                continue
            elif not skip:
                new_lines.append(line)

        # Get engines
        result = client.list_engines()
        engines = result.get("engines", [])

        if not engines:
            return False

        # Generate new entries
        config_entries = [managed_start]

        try:
            current_user = get_aws_username()
        except RuntimeError:
            # Not authenticated - can't determine user, skip filtering
            current_user = None

        for engine in engines:
            user = engine.get("user", "unknown")

            # Skip engines owned by other users (unless user is unknown or we can't determine current user)
            if current_user and user != "unknown" and user != current_user:
                continue

            instance_id = engine.get("instance_id")
            name = engine.get("name", instance_id)
            state = engine.get("state", "unknown")

            # Only add running engines
            if state != "running":
                continue

            config_entries.append(f"\nHost {name}\n")
            config_entries.append(f"    HostName {instance_id}\n")
            config_entries.append(f"    User {user}\n")
            config_entries.append(
                f"    ProxyCommand aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'\n"
            )

        config_entries.append(managed_end)

        # Write back
        new_lines.extend(config_entries)

        with open(ssh_config_path, "w") as f:
            f.writelines(new_lines)

        return True

    except Exception:
        return False


@click.group()
def engine_cli():
    """Manage engines."""
    pass


# ============================================================================
# Lifecycle Management
# ============================================================================


@engine_cli.command("launch")
@click.argument("name")
@click.option(
    "--type",
    "engine_type",
    required=True,
    type=click.Choice(
        ["cpu", "cpumax", "t4", "a10g", "a100", "4_t4", "8_t4", "4_a10g", "8_a10g"]
    ),
)
@click.option("--size", "boot_disk_size", type=int, help="Boot disk size in GB")
@click.option(
    "--no-wait", is_flag=True, help="Return immediately without waiting for readiness"
)
@click.option(
    "--skip-ssh-config", is_flag=True, help="Don't automatically update SSH config"
)
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def launch_engine(
    name: str,
    engine_type: str,
    boot_disk_size: Optional[int],
    no_wait: bool,
    skip_ssh_config: bool,
    env: str,
):
    """Launch a new engine and wait for it to be ready."""

    client = StudioManagerClient(environment=env)

    try:
        user = get_aws_username()
    except RuntimeError as e:
        click.echo(f"✗ {e}", err=True)
        raise click.Abort()

    click.echo(f"🚀 Launching {engine_type} engine '{name}'...")

    try:
        # Launch the engine
        engine = client.launch_engine(
            name=name, user=user, engine_type=engine_type, boot_disk_size=boot_disk_size
        )

        engine_id = engine["instance_id"]
        click.echo(f"✓ EC2 instance launched: {engine_id}")

        if no_wait:
            click.echo(f"\nEngine is initializing. Check status with:")
            click.echo(f"  dh engine status {name}")
            return

        # Wait for readiness with progress updates
        click.echo(f"\n⏳ Waiting for engine to be ready (typically 2-3 minutes)...\n")

        try:
            _final_status = wait_with_progress(
                status_func=lambda: client.get_engine_readiness(engine_id),
                is_complete_func=lambda s: s.get("ready", False),
                label="Progress",
                timeout_seconds=600,
            )

            click.echo(f"\n✓ Engine ready!")

            # Update SSH config unless skipped
            if not skip_ssh_config:
                if _update_ssh_config_silent(client, env):
                    click.echo("✓ SSH config updated")

            click.echo(f"\nConnect with:")
            click.echo(f"  dh studio attach {name}")
            click.echo(f"  dh engine ssh {name}")

        except TimeoutError:
            click.echo(f"\n⚠ Engine is still initializing. Check status with:")
            click.echo(f"  dh engine status {name}")

    except Exception as e:
        click.echo(f"✗ Failed to launch engine: {e}", err=True)
        raise click.Abort()


@engine_cli.command("start")
@click.argument("name_or_id")
@click.option(
    "--no-wait", is_flag=True, help="Return immediately without waiting for readiness"
)
@click.option(
    "--skip-ssh-config", is_flag=True, help="Don't automatically update SSH config"
)
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def start_engine(name_or_id: str, no_wait: bool, skip_ssh_config: bool, env: str):
    """Start a stopped engine."""

    client = StudioManagerClient(environment=env)

    try:
        # Find engine
        engine = client.get_engine_by_name(name_or_id)
        if not engine:
            engine = {"instance_id": name_or_id, "name": name_or_id}

        engine_id = engine["instance_id"]
        engine_name = engine.get("name", engine_id)

        click.echo(f"Starting engine '{engine_name}'...")

        result = client.start_engine(engine_id)

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        click.echo(f"✓ Engine '{engine_name}' is starting")

        if no_wait:
            click.echo(f"\nCheck status with:")
            click.echo(f"  dh engine status {engine_name}")
            return

        # Wait for engine to be running and fully ready (including status checks)
        click.echo(f"\n⏳ Waiting for engine to be ready...\n")

        try:

            def check_engine_running():
                """Check if engine is running, status checks passed, and SSM is accessible."""
                # Check EC2 state and status checks
                instance_status = client.check_instance_status(engine_id)
                if "error" in instance_status:
                    return {"ready": False, "progress_percent": 0}

                state = instance_status.get("state", "unknown")
                status_checks_passed = instance_status.get("reachable", False)

                # Check SSM accessibility via idle state
                engine_status = client.get_engine_status(engine_id)
                ssm_working = (
                    not ("error" in engine_status)
                    and engine_status.get("idle_state") is not None
                )

                # Progress based on state and checks
                if state == "pending":
                    progress = 30
                elif state == "running" and not status_checks_passed:
                    # Running but status checks still initializing
                    progress = 60
                elif state == "running" and status_checks_passed and not ssm_working:
                    # Status checks passed but SSM not yet responding
                    progress = 85
                elif state == "running" and status_checks_passed and ssm_working:
                    # Fully ready
                    progress = 100
                else:
                    progress = 10

                # Ready when running AND status checks pass AND SSM works
                ready = state == "running" and status_checks_passed and ssm_working

                return {"ready": ready, "progress_percent": progress}

            _final_status = wait_with_progress(
                status_func=check_engine_running,
                is_complete_func=lambda s: s.get("ready", False),
                label="Starting",
                timeout_seconds=300,
                show_stages=False,
            )

            click.echo(f"\n✓ Engine ready!")

            # Update SSH config unless skipped
            if not skip_ssh_config:
                if _update_ssh_config_silent(client, env):
                    click.echo("✓ SSH config updated")

            click.echo(f"\nConnect with:")
            click.echo(f"  dh studio attach {engine_name}")
            click.echo(f"  dh engine ssh {engine_name}")

        except TimeoutError:
            click.echo(f"\n⚠ Engine is still starting. Check status with:")
            click.echo(f"  dh engine status {engine_name}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@engine_cli.command("stop")
@click.argument("name_or_id")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def stop_engine(name_or_id: str, env: str):
    """Stop a running engine."""

    client = StudioManagerClient(environment=env)

    try:
        # Find engine
        engine = client.get_engine_by_name(name_or_id)
        if not engine:
            engine = {"instance_id": name_or_id, "name": name_or_id}

        engine_id = engine["instance_id"]
        engine_name = engine.get("name", engine_id)

        click.echo(f"Stopping engine '{engine_name}'...")

        result = client.stop_engine(engine_id)

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        click.echo(f"✓ Engine '{engine_name}' is stopping")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@engine_cli.command("terminate")
@click.argument("name_or_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def terminate_engine(name_or_id: str, yes: bool, env: str):
    """Terminate an engine."""

    client = StudioManagerClient(environment=env)

    try:
        # Find engine
        engine = client.get_engine_by_name(name_or_id)
        if not engine:
            engine = {"instance_id": name_or_id, "name": name_or_id}

        engine_id = engine["instance_id"]
        engine_name = engine.get("name", engine_id)

        # Confirm
        if not yes:
            if not click.confirm(f"Terminate engine '{engine_name}' ({engine_id})?"):
                click.echo("Cancelled")
                return

        # Terminate
        result = client.terminate_engine(engine_id)

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        click.echo(f"✓ Engine '{engine_name}' is terminating")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Status and Information
# ============================================================================


@engine_cli.command("status")
@click.argument("name_or_id")
@click.option("--detailed", is_flag=True, help="Show detailed sensor information")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def engine_status(name_or_id: str, detailed: bool, env: str):
    """Show engine status including idle detector state."""

    client = StudioManagerClient(environment=env)

    try:
        # Try to find by name first
        engine = client.get_engine_by_name(name_or_id)
        if not engine:
            # Assume it's an instance ID
            engine = {"instance_id": name_or_id, "name": name_or_id}

        engine_id = engine["instance_id"]

        # Get full status
        status_data = client.get_engine_status(engine_id)

        if "error" in status_data:
            click.echo(f"✗ Error: {status_data['error']}", err=True)
            raise click.Abort()

        # Display basic info
        engine_name = status_data.get("name", engine_id)
        click.echo(f"Engine: \033[34m{engine_name}\033[0m")  # Blue engine name
        click.echo(f"Instance ID: {engine_id}")
        click.echo(f"Type: {status_data.get('instance_type', 'unknown')}")

        # Show state in red if stopped, normal otherwise
        engine_state = status_data.get("state", "unknown")
        if engine_state.lower() in ["stopped", "stopping", "terminated", "terminating"]:
            click.echo(f"State: \033[31m{engine_state}\033[0m")  # Red for stopped
        else:
            click.echo(f"State: {engine_state}")

        if status_data.get("public_ip"):
            click.echo(f"Public IP: {status_data['public_ip']}")

        if status_data.get("launch_time"):
            click.echo(f"Launched: {format_time_ago(status_data['launch_time'])}")

        # Check if engine is stopped - don't show idle state or activity sensors
        if engine_state.lower() in ["stopped", "stopping", "terminated", "terminating"]:
            return

        # Show readiness if not ready
        if status_data.get("readiness"):
            readiness = status_data["readiness"]
            if not readiness.get("ready"):
                click.echo(
                    f"\n⏳ Initialization: {readiness.get('progress_percent', 0)}%"
                )
                click.echo(
                    f"Current Stage: {readiness.get('current_stage', 'unknown')}"
                )
                if readiness.get("estimated_time_remaining_seconds"):
                    remaining = readiness["estimated_time_remaining_seconds"]
                    click.echo(f"Estimated Time Remaining: {remaining}s")

        # Show idle state (only for running engines)
        if status_data.get("idle_state"):
            attached_studios = status_data.get("attached_studios", [])
            click.echo(
                f"\n{format_idle_state(status_data['idle_state'], detailed=detailed, attached_studios=attached_studios)}"
            )

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@engine_cli.command("list")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def list_engines(env: str):
    """List all engines."""

    client = StudioManagerClient(environment=env)

    try:
        result = client.list_engines()
        engines = result.get("engines", [])

        if not engines:
            click.echo("No engines found")
            return

        # Table header
        click.echo(f"{'Name':<30} {'Instance ID':<20} {'Type':<15} {'State':<10}")
        click.echo("-" * 80)

        # Table rows
        for engine in engines:
            name = engine.get("name", "unknown")[:29]
            instance_id = engine.get("instance_id", "unknown")
            engine_type = engine.get("engine_type", "unknown")
            state = engine.get("state", "unknown")

            click.echo(f"{name:<30} {instance_id:<20} {engine_type:<15} {state:<10}")

        click.echo(f"\nTotal: {len(engines)} engine(s)")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Access (SSH Config Management)
# ============================================================================


@engine_cli.command("config-ssh")
@click.option("--clean", is_flag=True, help="Remove all managed entries")
@click.option("--all", is_flag=True, help="Include engines from all users")
@click.option(
    "--admin",
    is_flag=True,
    help="Generate entries using ec2-user instead of owner",
)
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def config_ssh(clean: bool, all: bool, admin: bool, env: str):
    """Update SSH config with available engines."""

    client = StudioManagerClient(environment=env)
    ssh_config_path = os.path.expanduser("~/.ssh/config")

    try:
        # Read existing config
        if os.path.exists(ssh_config_path):
            with open(ssh_config_path, "r") as f:
                lines = f.readlines()
        else:
            lines = []

        # Remove managed entries
        managed_start = "# BEGIN DAYHOFF ENGINES\n"
        managed_end = "# END DAYHOFF ENGINES\n"

        new_lines = []
        skip = False
        for line in lines:
            if line == managed_start:
                skip = True
            elif line == managed_end:
                skip = False
                continue
            elif not skip:
                new_lines.append(line)

        if clean:
            # Write back without managed section
            with open(ssh_config_path, "w") as f:
                f.writelines(new_lines)
            click.echo("✓ Removed managed engine entries from SSH config")
            return

        # Get engines
        result = client.list_engines()
        engines = result.get("engines", [])

        if not engines:
            click.echo("No engines found")
            return

        # Generate new entries
        config_entries = [managed_start]

        try:
            current_user = get_aws_username()
        except RuntimeError:
            # Not authenticated - can't determine user
            current_user = None

        for engine in engines:
            user = engine.get("user", "unknown")

            # Skip if not all and not owned by current user (unless user is unknown or we can't determine current user)
            if not all and current_user and user != "unknown" and user != current_user:
                continue

            instance_id = engine.get("instance_id")
            name = engine.get("name", instance_id)
            state = engine.get("state", "unknown")

            # Only add running engines
            if state != "running":
                continue

            username = "ec2-user" if admin else user

            config_entries.append(f"\nHost {name}\n")
            config_entries.append(f"    HostName {instance_id}\n")
            config_entries.append(f"    User {username}\n")
            config_entries.append(
                f"    ProxyCommand aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'\n"
            )

        config_entries.append(managed_end)

        # Write back
        new_lines.extend(config_entries)

        with open(ssh_config_path, "w") as f:
            f.writelines(new_lines)

        click.echo(f"✓ Updated SSH config with {len(engines)} engine(s)")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Idle Detection Control
# ============================================================================


@engine_cli.command("coffee")
@click.argument("name_or_id")
@click.argument("duration", required=False)
@click.option("--cancel", is_flag=True, help="Cancel existing coffee lock")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def coffee(name_or_id: str, duration: Optional[str], cancel: bool, env: str):
    """Keep engine awake for specified duration (e.g., '4h', '2h30m')."""

    client = StudioManagerClient(environment=env)

    try:
        # Find engine
        engine = client.get_engine_by_name(name_or_id)
        if not engine:
            engine = {"instance_id": name_or_id, "name": name_or_id}

        engine_id = engine["instance_id"]
        engine_name = engine.get("name", engine_id)

        if cancel:
            result = client.cancel_coffee(engine_id)
            if "error" in result:
                click.echo(f"✗ Error: {result['error']}", err=True)
                raise click.Abort()
            click.echo(f"✓ Coffee lock cancelled for '{engine_name}'")
        else:
            if not duration:
                click.echo("✗ Error: duration required (e.g., '4h', '2h30m')", err=True)
                raise click.Abort()

            result = client.set_coffee(engine_id, duration)
            if "error" in result:
                click.echo(f"✗ Error: {result['error']}", err=True)
                raise click.Abort()
            click.echo(f"✓ Coffee lock set for '{engine_name}': {duration}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@engine_cli.command("idle")
@click.argument("name_or_id")
@click.option("--set", "set_timeout", help="Set new timeout (e.g., '2h30m', '45m')")
@click.option(
    "--slack",
    type=click.Choice(["none", "default", "all"]),
    help="Set Slack notifications",
)
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def idle_timeout_cmd(
    name_or_id: str, set_timeout: Optional[str], slack: Optional[str], env: str
):
    """Show or configure idle detector settings."""

    client = StudioManagerClient(environment=env)

    try:
        # Find engine
        engine = client.get_engine_by_name(name_or_id)
        if not engine:
            engine = {"instance_id": name_or_id, "name": name_or_id}

        engine_id = engine["instance_id"]
        engine_name = engine.get("name", engine_id)

        # Get current settings
        status = client.get_engine_status(engine_id)

        if "error" in status:
            click.echo(f"✗ Error: {status['error']}", err=True)
            raise click.Abort()

        # Update if requested
        if set_timeout or slack:
            result = client.update_idle_settings(
                engine_id, timeout=set_timeout, slack=slack
            )
            if "error" in result:
                click.echo(f"✗ Error: {result['error']}", err=True)
                raise click.Abort()
            click.echo(f"✓ Idle settings updated for '{engine_name}'")

        # Show current settings
        idle_state = status.get("idle_state", {})
        timeout_seconds = idle_state.get("timeout_seconds", 1800)
        timeout_minutes = timeout_seconds // 60

        click.echo(f"\nIdle Settings for '{engine_name}':")
        click.echo(f"  Timeout: {timeout_minutes} minutes")
        click.echo(
            f"  Current State: {'IDLE' if idle_state.get('is_idle') else 'ACTIVE'}"
        )

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Maintenance
# ============================================================================


@engine_cli.command("resize")
@click.argument("name_or_id")
@click.option("--size", "-s", required=True, type=int, help="New size in GB")
@click.option(
    "--online",
    is_flag=True,
    help="Resize while running (requires manual filesystem expansion)",
)
@click.option("--force", "-f", is_flag=True, help="Force resize")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def resize_engine(name_or_id: str, size: int, online: bool, force: bool, env: str):
    """Resize an engine's boot disk."""

    client = StudioManagerClient(environment=env)

    try:
        # Find engine
        engine = client.get_engine_by_name(name_or_id)
        if not engine:
            engine = {"instance_id": name_or_id, "name": name_or_id}

        engine_id = engine["instance_id"]
        engine_name = engine.get("name", engine_id)

        if not force:
            if not click.confirm(f"Resize boot disk of '{engine_name}' to {size}GB?"):
                click.echo("Cancelled")
                return

        result = client.resize_engine(engine_id, size, online)

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        click.echo(f"✓ Boot disk resize initiated for '{engine_name}'")
        if online:
            click.echo("  Note: Manual filesystem expansion required")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@engine_cli.command("gami")
@click.argument("name_or_id")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def create_ami(name_or_id: str, env: str):
    """Create a Golden AMI from an engine."""

    client = StudioManagerClient(environment=env)

    try:
        # Find engine
        engine = client.get_engine_by_name(name_or_id)
        if not engine:
            engine = {"instance_id": name_or_id, "name": name_or_id}

        engine_id = engine["instance_id"]
        engine_name = engine.get("name", engine_id)

        click.echo(f"Creating Golden AMI from '{engine_name}'...")

        result = client.create_ami(engine_id)

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        ami_id = result.get("ami_id")
        click.echo(f"✓ AMI creation started: {ami_id}")
        click.echo(f"  This will take several minutes")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@engine_cli.command("debug")
@click.argument("name_or_id")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def debug_engine(name_or_id: str, env: str):
    """Debug engine bootstrap status and files."""

    client = StudioManagerClient(environment=env)

    try:
        # Find engine
        engine = client.get_engine_by_name(name_or_id)
        if not engine:
            engine = {"instance_id": name_or_id, "name": name_or_id}

        engine_id = engine["instance_id"]

        # Get readiness status
        readiness = client.get_engine_readiness(engine_id)

        click.echo(f"Engine: {engine_id}")
        click.echo(f"Ready: {readiness.get('ready', False)}")
        click.echo(f"Current Stage: {readiness.get('current_stage', 'unknown')}")
        click.echo(f"\nBootstrap Stages:")

        stages = readiness.get("stages", [])
        for i, stage in enumerate(stages, 1):
            status = stage.get("status", "unknown")
            name = stage.get("name", "unknown")
            duration = (
                stage.get("duration_ms", 0) / 1000 if stage.get("duration_ms") else None
            )

            icon = (
                "✓"
                if status == "completed"
                else "⏳" if status == "in_progress" else "✗"
            )
            duration_str = f" ({duration:.1f}s)" if duration else ""

            click.echo(f"  {icon} {i}. {name}{duration_str}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()
