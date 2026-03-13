#!/usr/bin/env python3
"""
cli-anything-godzilla: CLI harness for Godzilla WebShell Manager.

A stateful CLI interface that allows AI agents to operate Godzilla
without needing a GUI.
"""

import click
import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    import yaml
except ImportError:
    yaml = None

from cli_anything.godzilla.core.project import (
    create_project,
    open_project,
    save_project,
    close_project,
    get_project_info,
    list_projects,
    get_current_project,
)
from cli_anything.godzilla.core.shell import (
    add_shell,
    update_shell,
    remove_shell,
    list_shells,
    get_shell,
    test_shell,
    export_shells,
    import_shells,
    ShellEntity,
)
from cli_anything.godzilla.core.profile import (
    load_profile,
    list_profiles,
    validate_profile,
    C2Profile,
)
from cli_anything.godzilla.utils.repl_skin import ReplSkin


# Global context
@click.group(invoke_without_command=True)
@click.option("-p", "--project", "project_path", help="Path to project file")
@click.option("--jar", "--jar-path", "jar_path", help="Path to Godzilla JAR file")
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
@click.pass_context
def cli(ctx, project_path: str, jar_path: str, json_output: bool):
    """Main CLI entry point."""
    ctx.ensure_object(dict)
    ctx.obj["project"] = project_path
    ctx.obj["jar_path"] = jar_path
    ctx.obj["json_flag"] = json_output

    # Open project if path specified
    if project_path:
        try:
            open_project(project_path)
        except Exception as e:
            click.echo(f"Error opening project: {e}", err=True)

    # If no subcommand, enter REPL mode
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command()
def version():
    """Show version information."""
    click.echo("cli-anything-godzilla v1.0.0")
    click.echo("\033[36mA CLI harness for Godzilla Security Testing Tool\033[0m")


@cli.command()
def help_cmd():
    """Show comprehensive help."""
    help_text = """
\033[36mcli-anything-godzilla\033[0m - CLI harness for Godzilla Security Testing Tool

\033[33mCommands:\033[0m
  \033[32mproject\033[0m   Project management (create, open, save, info)
  \033[32mshell\033[0m     Shell management (add, list, test, export, import)
  \033[32mprofile\033[0m  C2 Profile management (load, save, validate)
  \033[32mrepl\033[0m      Interactive REPL mode
  \033[32mversion\033[0m   Show version information

\033[33mExamples:\033[0m
  # Create a new project
  cli-anything-godzilla project new my-project

  # Open existing project
  cli-anything-godzilla project open ./project.json

  # Add a shell interactively
  cli-anything-godzilla

  # List shells
  cli-anything-godzilla shell list

\033[33mGlobal Options:\033[0m
  -p, --project    Path to project file
  --jar            Path to Godzilla JAR file
  --json           Output in JSON format
"""
    click.echo(help_text)


# Project commands group
@cli.group("project")
def project_cli():
    """Project management commands."""
    pass


@project_cli.command("new")
@click.option("-n", "--name", required=True, help="Project name")
@click.option("-d", "--description", default="", help="Project description")
@click.option("-o", "--output", "output_path", help="Output directory path")
def project_new(name: str, description: str, output_path: Optional[str]):
    """Create a new project."""
    try:
        project = create_project(name=name, path=output_path, description=description)
        skin = ReplSkin("godzilla", "1.0.0")
        skin.success(f"Created project: {name}")
        skin.status("Path", str(project.project_path))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project_cli.command("open")
@click.argument("path", required=True)
def project_open(path: str):
    """Open an existing project."""
    try:
        project = open_project(path)
        skin = ReplSkin("godzilla", "1.0.0")
        skin.success(f"Opened project: {project.name}")
        skin.status("Path", path)
    except FileNotFoundError:
        click.echo(f"Project not found: {path}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project_cli.command("info")
@click.pass_context
def project_info(ctx):
    """Show current project information."""
    project = get_current_project()
    if not project:
        click.echo("No project open. Use 'project open' first.")
        return

    info = get_project_info(project)
    if ctx.obj.get("json_flag"):
        click.echo(json.dumps(info, indent=2))
    else:
        skin = ReplSkin("godzilla", "1.0.0")
        skin.status("Name", info.get("name", "N/A"))
        skin.status("Path", info.get("path", "N/A"))
        skin.status("Shells", str(info.get("shell_count", 0)))


@project_cli.command("list")
@click.pass_context
def project_list(ctx):
    """List all projects."""
    projects = list_projects()
    if ctx.obj.get("json_flag"):
        click.echo(json.dumps(projects, indent=2))
    else:
        skin = ReplSkin("godzilla", "1.0.0")
        if not projects:
            skin.info("No projects found")
            return
        for p in projects:
            click.echo(f"  {p['name']}: {p['path']}")


@project_cli.command("close")
def project_close_cmd():
    """Close current project."""
    project = get_current_project()
    if not project:
        click.echo("No project open.")
        return
    close_project(project)
    skin = ReplSkin("godzilla", "1.0.0")
    skin.success("Project closed")


# Shell commands group
@cli.group("shell")
def shell_cli():
    """Shell management commands."""
    pass


@shell_cli.command("add")
@click.option("-u", "--url", required=True, help="Shell URL")
@click.option("-p", "--password", required=True, help="Shell password")
@click.option("-k", "--secret-key", default="", help="Secret key")
@click.option("--payload", default="JavaDynamicPayload", help="Payload type")
@click.option("--cryption", default="xor", help="Encryption method")
@click.option("--encoding", default="UTF-8", help="Character encoding")
@click.option("--remark", default="", help="Shell remark")
@click.pass_context
def shell_add(ctx, url: str, password: str, secret_key: str, payload: str, cryption: str, encoding: str, remark: str):
    """Add a new shell."""
    project = get_current_project()
    if not project:
        click.echo("No project open. Use 'project open' first.", err=True)
        sys.exit(1)

    try:
        shell = add_shell(
            url=url,
            password=password,
            secret_key=secret_key,
            payload=payload,
            cryption=cryption,
            encoding=encoding,
            remark=remark,
        )
        skin = ReplSkin("godzilla", "1.0.0")
        skin.success(f"Added shell: {shell.id}")
        skin.status("URL", shell.url)
        skin.status("Payload", shell.payload)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@shell_cli.command("list")
@click.pass_context
def shell_list(ctx):
    """List all shells."""
    project = get_current_project()
    if not project:
        click.echo("No project open. Use 'project open' first.", err=True)
        return

    shells = list_shells()
    if ctx.obj.get("json_flag"):
        output = [s.to_dict() for s in shells]
        click.echo(json.dumps(output, indent=2))
    else:
        skin = ReplSkin("godzilla", "1.0.0")
        if not shells:
            skin.info("No shells configured")
            return
        for s in shells:
            click.echo(f"  {s.id[:8]}: {s.url} ({s.payload})")


@shell_cli.command("get")
@click.argument("shell_id", required=True)
@click.pass_context
def shell_get(ctx, shell_id: str):
    """Get shell details."""
    project = get_current_project()
    if not project:
        click.echo("No project open. Use 'project open' first.", err=True)
        return

    shell = get_shell(shell_id)
    if not shell:
        click.echo(f"Shell not found: {shell_id}", err=True)
        return

    if ctx.obj.get("json_flag"):
        click.echo(json.dumps(shell.to_dict(), indent=2))
    else:
        skin = ReplSkin("godzilla", "1.0.0")
        skin.status("ID", shell.id)
        skin.status("URL", shell.url)
        skin.status("Payload", shell.payload)
        skin.status("Cryption", shell.cryption)


@shell_cli.command("update")
@click.argument("shell_id", required=True)
@click.option("--url", help="Update URL")
@click.option("--password", help="Update password")
@click.option("--remark", help="Update remark")
@click.pass_context
def shell_update(ctx, shell_id: str, url: Optional[str], password: Optional[str], remark: Optional[str]):
    """Update shell configuration."""
    project = get_current_project()
    if not project:
        click.echo("No project open. Use 'project open' first.", err=True)
        return

    kwargs = {}
    if url:
        kwargs["url"] = url
    if password:
        kwargs["password"] = password
    if remark:
        kwargs["remark"] = remark

    if not kwargs:
        click.echo("No updates specified.")
        return

    success = update_shell(shell_id, **kwargs)
    if success:
        skin = ReplSkin("godzilla", "1.0.0")
        skin.success(f"Updated shell: {shell_id}")
    else:
        click.echo(f"Shell not found: {shell_id}", err=True)


@shell_cli.command("remove")
@click.argument("shell_id", required=True)
@click.pass_context
def shell_remove(ctx, shell_id: str):
    """Remove a shell."""
    project = get_current_project()
    if not project:
        click.echo("No project open. Use 'project open' first.", err=True)
        return

    success = remove_shell(shell_id)
    if success:
        skin = ReplSkin("godzilla", "1.0.0")
        skin.success(f"Removed shell: {shell_id}")
    else:
        click.echo(f"Shell not found: {shell_id}", err=True)


@shell_cli.command("test")
@click.argument("shell_id", required=True)
@click.pass_context
def shell_test_cmd(ctx, shell_id: str):
    """Test shell connectivity."""
    project = get_current_project()
    if not project:
        click.echo("No project open. Use 'project open' first.", err=True)
        return

    result = test_shell(shell_id)
    if ctx.obj.get("json_flag"):
        click.echo(json.dumps(result, indent=2))
    else:
        skin = ReplSkin("godzilla", "1.0.0")
        if result.get("success"):
            skin.success("Shell connection successful")
        else:
            skin.error(f"Shell connection failed: {result.get('error')}")


@shell_cli.command("export")
@click.argument("output", required=True)
@click.option("-i", "--ids", help="Comma-separated shell IDs")
@click.pass_context
def shell_export(ctx, output: str, ids: Optional[str]):
    """Export shells to JSON file."""
    project = get_current_project()
    if not project:
        click.echo("No project open. Use 'project open' first.", err=True)
        return

    shell_ids = ids.split(",") if ids else None
    export_shells(output, shell_ids)
    skin = ReplSkin("godzilla", "1.0.0")
    skin.success(f"Exported shells to {output}")


@shell_cli.command("import")
@click.argument("input_file", required=True)
@click.option("--overwrite", is_flag=True, help="Overwrite existing shells")
@click.pass_context
def shell_import(ctx, input_file: str, overwrite: bool):
    """Import shells from JSON file."""
    project = get_current_project()
    if not project:
        click.echo("No project open. Use 'project open' first.", err=True)
        return

    count = import_shells(input_file, overwrite)
    skin = ReplSkin("godzilla", "1.0.0")
    skin.success(f"Imported {count} shells")


# Profile commands group
@cli.group("profile")
def profile_cli():
    """C2 Profile management commands."""
    pass


@profile_cli.command("list")
@click.pass_context
def profile_list(ctx):
    """List available C2 profiles."""
    project = get_current_project()
    profiles = []

    if project and project.is_open:
        profile_dir = Path(project.project_path) / "profile"
        if profile_dir.exists():
            for f in profile_dir.glob("*.profile"):
                profiles.append({
                    "name": f.stem,
                    "path": str(f),
                })

    if ctx.obj.get("json_flag"):
        click.echo(json.dumps(profiles, indent=2))
    else:
        skin = ReplSkin("godzilla", "1.0.0")
        if not profiles:
            skin.info("No profiles found")
        else:
            for p in profiles:
                click.echo(f"  {p['name']}: {p['path']}")


@profile_cli.command("load")
@click.argument("path", required=True)
@click.pass_context
def profile_load(ctx, path: str):
    """Load a C2 profile from file."""
    try:
        profile = load_profile(path)
        skin = ReplSkin("godzilla", "1.0.0")
        skin.success(f"Loaded profile: {profile.name}")
        if ctx.obj.get("json_flag"):
            click.echo(json.dumps(profile.to_dict(), indent=2))
    except Exception as e:
        click.echo(f"Error loading profile: {e}", err=True)
        sys.exit(1)


@profile_cli.command("validate")
@click.argument("path", required=True)
@click.pass_context
def profile_validate(ctx, path: str):
    """Validate a C2 profile file."""
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f) if yaml else {}
        errors = validate_profile(data)
        if ctx.obj.get("json_flag"):
            click.echo(json.dumps({"valid": len(errors) == 0, "errors": errors}, indent=2))
        else:
            skin = ReplSkin("godzilla", "1.0.0")
            if errors:
                skin.error("Profile validation failed:")
                for err in errors:
                    click.echo(f"  - {err}")
            else:
                skin.success("Profile is valid")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# REPL command
@cli.command("repl")
@click.option("-p", "--project", "project_path", help="Path to project file")
@click.pass_context
def repl(ctx, project_path: Optional[str]):
    """Start interactive REPL mode."""
    # Load project if specified
    if project_path:
        try:
            open_project(project_path)
        except Exception as e:
            click.echo(f"Error opening project: {e}", err=True)

    current_project = get_current_project()
    skin = ReplSkin("godzilla", "1.0.0")
    skin.print_banner()

    if current_project:
        skin.info(f"Project: {current_project.name}")

    # Command registry for help
    commands = {
        "help": "Show this help",
        "exit": "Exit REPL",
        "project info": "Show project information",
        "project list": "List all projects",
        "shell list": "List all shells",
        "shell get <id>": "Get shell details",
        "shell add <url> <password>": "Add new shell",
        "shell test <id>": "Test shell connectivity",
        "profile list": "List C2 profiles",
    }

    skin.info("Type 'help' for available commands")

    # Simple REPL loop
    while True:
        try:
            line = input("godzilla> ")
            if not line:
                continue

            line = line.strip()
            if not line:
                continue

            # Handle commands
            if line in ["exit", "quit", "q"]:
                skin.print_goodbye()
                break
            elif line in ["help", "h", "?"]:
                skin.help(commands)
            elif line == "project info":
                ctx.invoke(project_info)
            elif line == "project list":
                ctx.invoke(project_list)
            elif line == "shell list":
                ctx.invoke(shell_list)
            elif line.startswith("shell get "):
                # 支持 shell_id (支持短ID)
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    shell_id = parts[2].strip()
                    ctx.invoke(shell_get, shell_id=shell_id)
            elif line.startswith("shell add "):
                # Support url and password
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    url = parts[1].strip()
                    password = parts[2].strip()
                    ctx.invoke(shell_add, url=url, password=password)
            elif line.startswith("shell test "):
                # support shell_id (支持短ID)
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    shell_id = parts[2].strip()
                    ctx.invoke(shell_test_cmd, shell_id=shell_id)
            elif line.startswith("shell update "):
                # support shell update with short ID
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    shell_id = parts[2].strip()
                    # 简单的更新，只支持 shell update <id> --remark "xxx" 格式
                    if " --remark " in line:
                        remark_parts = line.split(" --remark ", 1)
                        remark = remark_parts[1].strip().strip('"')
                        ctx.invoke(shell_update, shell_id=shell_id, remark=remark)
            elif line.startswith("shell remove "):
                # support shell remove with short ID
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    shell_id = parts[2].strip()
                    ctx.invoke(shell_remove, shell_id=shell_id)
            elif line == "profile list":
                ctx.invoke(profile_list)
            else:
                skin.error(f"Unknown command: {line}")
                skin.info("Type 'help' for available commands")

        except KeyboardInterrupt:
            skin.print_goodbye()
            break
        except Exception as e:
            skin.error(f"Error: {e}")


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
