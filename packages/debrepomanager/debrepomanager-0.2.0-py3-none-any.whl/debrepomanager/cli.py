"""Command-line interface for Debian Repository Manager.

This module provides the main CLI entry point using Click.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

import click

from debrepomanager.aptly import AptlyError, AptlyManager
from debrepomanager.config import Config, ConfigError
from debrepomanager.utils import find_deb_files, setup_logging

logger = logging.getLogger(__name__)


def _collect_package_files(
    packages: tuple, package_dir: Optional[str], verbose: bool
) -> List[str]:
    """Collect package files from arguments.

    Args:
        packages: Tuple of package file paths
        package_dir: Optional directory containing packages
        verbose: Whether to print verbose messages

    Returns:
        List of package file paths

    Raises:
        click.ClickException: If package collection fails
    """
    pkg_files: List[str] = list(packages)

    if package_dir:
        try:
            found_files = find_deb_files(package_dir, recursive=True)
            pkg_files.extend(found_files)
            if verbose:
                click.echo(f"Found {len(found_files)} package(s) in {package_dir}")
        except (FileNotFoundError, ValueError) as e:
            raise click.ClickException(str(e))

    if not pkg_files:
        raise click.ClickException(
            "No packages specified. Use --packages or --package-dir"
        )

    return pkg_files


def _ensure_repo_exists(
    manager: AptlyManager, codename: str, component: str, force: bool, auto_create: bool
) -> None:
    """Ensure repository exists, creating if needed.

    Args:
        manager: AptlyManager instance
        codename: Distribution codename
        component: Repository component
        force: Whether to force creation
        auto_create: Whether auto-create is enabled

    Raises:
        click.ClickException: If repo doesn't exist and can't be created
    """
    if not manager.repo_exists(codename, component):
        if force or auto_create:
            click.echo(f"Repository {component} doesn't exist, creating...")
            manager.create_repo(codename, component)
            click.echo("✓ Repository created")
        else:
            raise click.ClickException(
                f"Repository {codename}/{component} doesn't exist. "
                "Use --force to create or enable auto_create in config."
            )


@click.group()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging (DEBUG level)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Simulate operations without making changes",
)
@click.pass_context
def cli(
    ctx: click.Context, config: Optional[str], verbose: bool, dry_run: bool
) -> None:
    """Debian Repository Manager - manage Debian-like repositories with aptly.

    Examples:

        \b
        # Add packages to repository
        repomanager add --codename bookworm --component jethome-tools --packages *.deb

        \b
        # Create new repository
        repomanager create-repo --codename noble --component jethome-armbian

        \b
        # List repositories
        repomanager list --codename bookworm
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    ctx.obj["logger"] = setup_logging(level=log_level)
    ctx.obj["verbose"] = verbose
    ctx.obj["dry_run"] = dry_run

    # Load configuration
    try:
        ctx.obj["config"] = Config(config)
        if verbose:
            click.echo(f"Loaded configuration from: {config or 'default locations'}")
    except ConfigError as e:
        click.echo(f"Error: Configuration error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--codename",
    required=True,
    help="Distribution codename (e.g., bookworm, noble, trixie)",
)
@click.option(
    "--component",
    required=True,
    help="Repository component (e.g., jethome-tools, jethome-armbian)",
)
@click.option(
    "--packages",
    multiple=True,
    type=click.Path(exists=True),
    help="Package files to add (can be specified multiple times)",
)
@click.option(
    "--package-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory containing .deb packages (searched recursively)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Create repository if it doesn't exist (even if auto_create is disabled)",
)
@click.pass_context
def add(
    ctx: click.Context,
    codename: str,
    component: str,
    packages: tuple,
    package_dir: Optional[str],
    force: bool,
) -> None:
    """Add packages to repository with atomic snapshot publication.

    Examples:

        \b
        # Add specific packages
        repomanager add --codename bookworm --component jethome-tools \\
            --packages pkg1.deb --packages pkg2.deb

        \b
        # Add all packages from directory
        repomanager add --codename bookworm --component jethome-tools \\
            --package-dir /path/to/packages/

        \b
        # Force create repository if doesn't exist
        repomanager add --codename bookworm --component jethome-tools \\
            --package-dir /path/to/packages/ --force
    """
    config: Config = ctx.obj["config"]
    dry_run: bool = ctx.obj["dry_run"]
    verbose: bool = ctx.obj["verbose"]

    # Collect package files
    try:
        pkg_files = _collect_package_files(packages, package_dir, verbose)
    except click.ClickException:
        raise

    if verbose:
        click.echo(f"Adding {len(pkg_files)} package(s) to {codename}/{component}")

    # Dry run mode
    if dry_run:
        click.echo("Dry-run mode: No changes will be made")
        click.echo(f"Would add {len(pkg_files)} package(s):")
        for pkg in pkg_files:
            click.echo(f"  - {Path(pkg).name}")
        return

    # Add packages
    try:
        manager = AptlyManager(config)
        _ensure_repo_exists(
            manager, codename, component, force, config.auto_create_repos
        )

        click.echo(f"Adding {len(pkg_files)} package(s)...")
        manager.add_packages(codename, component, pkg_files)

        click.echo("✓ Packages added successfully")
        click.echo(f"Repository: {codename}/{component}")

    except click.ClickException:
        raise
    except (AptlyError, ConfigError, FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        logger.exception("Unexpected error in add command")
        sys.exit(99)


@cli.command("create-repo")
@click.option(
    "--codename",
    required=True,
    help="Distribution codename (e.g., bookworm, noble)",
)
@click.option(
    "--component",
    required=True,
    help="Repository component (e.g., jethome-tools)",
)
@click.option(
    "--architectures",
    multiple=True,
    help="Architectures to support (default: from config)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Recreate repository if it already exists",
)
@click.pass_context
def create_repo(
    ctx: click.Context,
    codename: str,
    component: str,
    architectures: tuple,
    force: bool,
) -> None:
    """Create new repository.

    Examples:

        \b
        # Create repository with default architectures
        repomanager create-repo --codename bookworm --component jethome-tools

        \b
        # Create with specific architectures
        repomanager create-repo --codename bookworm --component test \\
            --architectures amd64 --architectures arm64

        \b
        # Force recreate if exists
        repomanager create-repo --codename bookworm --component test --force
    """
    config: Config = ctx.obj["config"]
    dry_run: bool = ctx.obj["dry_run"]

    if dry_run:
        click.echo("Dry-run mode: No changes will be made")
        click.echo(f"Would create repository: {codename}/{component}")
        if architectures:
            click.echo(f"Architectures: {', '.join(architectures)}")
        return

    try:
        manager = AptlyManager(config)

        archs = list(architectures) if architectures else None

        if ctx.obj["verbose"]:
            click.echo(f"Creating repository {codename}/{component}...")

        manager.create_repo(codename, component, architectures=archs, force=force)

        click.echo(f"✓ Repository created: {codename}/{component}")

    except ValueError as e:
        # Repository already exists
        click.echo(f"Error: {e}", err=True)
        click.echo("Hint: Use --force to recreate", err=True)
        sys.exit(1)
    except (AptlyError, ConfigError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("delete-repo")
@click.option(
    "--codename",
    required=True,
    help="Distribution codename",
)
@click.option(
    "--component",
    required=True,
    help="Repository component",
)
@click.option(
    "--confirm",
    is_flag=True,
    help="Confirm deletion (required for safety)",
)
@click.pass_context
def delete_repo(
    ctx: click.Context,
    codename: str,
    component: str,
    confirm: bool,
) -> None:
    """Delete repository and all its snapshots.

    Examples:

        \b
        # Delete repository (requires --confirm)
        repomanager delete-repo --codename bookworm --component old-repo --confirm
    """
    config: Config = ctx.obj["config"]
    dry_run: bool = ctx.obj["dry_run"]

    if dry_run:
        click.echo("Dry-run mode: No changes will be made")
        click.echo(f"Would delete repository: {codename}/{component}")
        return

    if not confirm:
        click.echo("Error: Repository deletion requires --confirm flag", err=True)
        click.echo(f"To delete {codename}/{component}, run:", err=True)
        click.echo(
            f"  repomanager delete-repo --codename {codename} --component {component} --confirm",
            err=True,
        )
        sys.exit(1)

    try:
        manager = AptlyManager(config)

        # Check if repository exists BEFORE confirmation prompt
        if not manager.repo_exists(codename, component):
            click.echo(
                f"Error: Repository {codename}/{component} doesn't exist", err=True
            )
            sys.exit(1)

        # Additional confirmation prompt
        click.echo(f"⚠️  WARNING: This will delete repository {codename}/{component}")
        click.echo("⚠️  This action cannot be undone!")

        if not click.confirm("Are you sure you want to continue?"):
            click.echo("Cancelled.")
            sys.exit(0)

        click.echo(f"Deleting repository {codename}/{component}...")
        manager.delete_repo(codename, component)

        click.echo(f"✓ Repository deleted: {codename}/{component}")

    except (AptlyError, ConfigError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("list")
@click.option(
    "--codename",
    help="Filter by distribution codename",
)
@click.option(
    "--component",
    help="Filter by component",
)
@click.pass_context
def list_repos(
    ctx: click.Context,
    codename: Optional[str],
    component: Optional[str],
) -> None:
    """List repositories and packages.

    Examples:

        \b
        # List all repositories
        repomanager list

        \b
        # List repos for specific codename
        repomanager list --codename bookworm

        \b
        # List packages in specific component
        repomanager list --codename bookworm --component jethome-tools
    """
    config: Config = ctx.obj["config"]

    try:
        manager = AptlyManager(config)

        if codename and component:
            # List packages in specific component
            if not manager.repo_exists(codename, component):
                click.echo(f"Repository {codename}/{component} doesn't exist", err=True)
                sys.exit(1)

            packages = manager.list_packages(codename, component)

            click.echo(f"Repository: {codename}/{component}")
            click.echo(f"Packages: {len(packages)}")
            click.echo()

            if packages:
                for pkg in packages:
                    click.echo(f"  {pkg}")
            else:
                click.echo("  (empty)")

        else:
            # List repositories
            if codename:
                repos = manager.list_repos(codename)
                click.echo(f"Repositories for {codename}:")
            else:
                repos = manager.list_repos()
                click.echo("All repositories:")

            click.echo(f"Total: {len(repos)}")
            click.echo()

            if repos:
                for repo in repos:
                    click.echo(f"  {repo}")
            else:
                click.echo("  (none)")

    except (AptlyError, ConfigError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def sync(ctx: click.Context) -> None:
    """Sync metadata with actual repository state.

    Scans all aptly roots to find existing repositories and rebuilds
    metadata from scratch. Useful after manual aptly operations or
    to recover from metadata corruption.

    Example:
        debrepomanager sync
    """
    verbose: bool = ctx.obj["verbose"]
    config: Config = ctx.obj["config"]

    try:
        manager = AptlyManager(config)

        if verbose:
            click.echo("Syncing metadata with actual repository state...")

        count = manager.sync_metadata()

        click.echo(f"✓ Synced {count} repositories")

        if verbose:
            # Show synced repositories
            repos = manager.metadata.list_repositories()
            if repos:
                click.echo("\nRepositories:")
                for repo in repos:
                    click.echo(f"  {repo['codename']}/{repo['component']}")

    except (AptlyError, ConfigError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--codename",
    required=True,
    help="Distribution codename (e.g., bookworm, noble)",
)
@click.option(
    "--component",
    required=True,
    help="Repository component (e.g., jethome-tools)",
)
@click.option(
    "--apply",
    is_flag=True,
    default=False,
    help="Actually remove packages (default is dry-run)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cleanup(  # noqa: C901
    ctx: click.Context,
    codename: str,
    component: str,
    apply: bool,
    verbose: bool,
) -> None:
    """Clean up old package versions based on retention policy.

    By default runs in DRY-RUN mode to show what would be removed.
    Use --apply to actually remove packages.

    The retention policy is configured in config.yaml:
    - min_versions: Minimum number of versions to keep (always preserved)
    - max_age_days: Maximum age in days (older packages removed if > min_versions)

    Examples:

        # Dry-run (show what would be removed):
        debrepomanager cleanup --codename bookworm --component jethome-tools

        # Actually remove packages:
        debrepomanager cleanup --codename bookworm --component jethome-tools --apply

        # With verbose output:
        debrepomanager cleanup --codename bookworm --component jethome-tools -v
    """
    from debrepomanager.retention import RetentionPolicy

    config: Config = ctx.obj["config"]
    # Setup logging with config level
    if verbose:
        setup_logging(level="DEBUG")
    else:
        setup_logging(level=config.logging_level)

    try:
        # Initialize managers
        aptly = AptlyManager(config)
        retention = RetentionPolicy(config, aptly)

        # Determine dry-run mode
        dry_run = not apply

        # Show mode
        if dry_run:
            click.echo("🔍 DRY RUN MODE - No packages will be removed\n")
        else:
            click.secho(
                "⚠️  APPLY MODE - Packages will be permanently removed!",
                fg="yellow",
                bold=True,
            )
            click.echo()

        # Get retention policy for component
        policy = retention.get_policy(component)
        click.echo(f"Retention Policy for {component}:")
        click.echo(f"  - Min versions to keep: {policy.get('min_versions', 'N/A')}")
        click.echo(f"  - Max age (days): {policy.get('max_age_days', 'N/A')}")
        click.echo()

        # Perform cleanup
        click.echo(f"Analyzing repository {codename}/{component}...")
        result = retention.cleanup(codename, component, dry_run=dry_run)

        # Display results
        click.echo()
        click.secho("📊 Cleanup Report:", bold=True)
        click.echo(f"  Packages analyzed: {result['analyzed']}")
        click.echo(f"  Packages to remove: {result['to_remove']}")

        if result["removed"] > 0:
            click.secho(
                f"  Packages removed: {result['removed']}", fg="green", bold=True
            )
        elif not dry_run and result["to_remove"] > 0:
            click.secho("  Packages removed: 0 (failed)", fg="red")

        click.echo(f"  Estimated space to free: ~{result['space_mb']} MB")

        # Show package list if verbose or dry-run
        if (verbose or dry_run) and result["packages"]:
            click.echo()
            click.echo("Packages to remove:")
            for pkg in result["packages"][:20]:  # Show first 20
                click.echo(f"  - {pkg}")
            if len(result["packages"]) > 20:
                click.echo(f"  ... and {len(result['packages']) - 20} more")

        # Final message
        click.echo()
        if dry_run and result["to_remove"] > 0:
            click.secho(
                "✨ Run with --apply to actually remove these packages",
                fg="cyan",
                bold=True,
            )
        elif not dry_run and result["removed"] > 0:
            click.secho("✅ Cleanup completed successfully!", fg="green", bold=True)
        elif result["to_remove"] == 0:
            click.secho("✨ No packages to remove - repository is clean!", fg="green")

    except (AptlyError, ConfigError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
