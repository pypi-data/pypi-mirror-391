"""Command line interface for hdc_installer."""

import click


@click.command()
@click.option("-h", "--help-flag", is_flag=True, help="Show help message and exit")
@click.option("-l", "--list-binaries", is_flag=True, help="List available HDC binaries")
@click.option("-i", "--install", is_flag=True, help="Install HDC binary")
def main(help_flag, list_binaries, install):
    """Main CLI entry point for hdc_installer."""
    if help_flag:
        click.echo("Usage: hdc_installer [OPTIONS]")
        click.echo("Options:")
        click.echo("  -h, --help-flag    Show help message and exit")
        click.echo("  -l, --list-binaries    List available HDC binaries")
        click.echo("  -i, --install Install HDC binary")
        return

    if list_binaries:
        click.echo("Available HDC binaries:")
        click.echo("  - hdc for Windows (x86_64)")
        click.echo("  - hdc for Linux (x86_64)")
        click.echo("  - hdc for macOS (x86_64)")
        click.echo("  - hdc for macOS (ARM64)")
        return

    if install:
        click.echo("Installing HDC binary...")
        # Implementation would go here
        click.echo("HDC binary installed successfully!")
        return

    # Default behavior when no options are provided
    click.echo("hdc_installer - A lightweight installer for HarmonyOS HDC tools")
    click.echo("Use -h for help, -l to list binaries, -i to install")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
