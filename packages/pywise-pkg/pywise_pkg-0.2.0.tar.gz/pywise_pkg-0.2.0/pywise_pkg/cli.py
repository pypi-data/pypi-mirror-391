"""
Enhanced command-line interface for pywise_pkg with advanced features
"""

import sys
import json
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@click.group()
@click.version_option(version="0.1.0", prog_name="pywise_pkg")
def cli():
    """
    pywise_pkg - Intelligent Python Dependency Management

    Advanced dependency management with conda-pip hybrid support,
    environment migration, and Docker optimization.
    """
    pass

@cli.command()
@click.option('--format', 'output_format', default='pip', 
              type=click.Choice(['pip', 'conda', 'poetry', 'pipenv']),
              help='Output format for dependencies')
@click.option('--output', '-o', type=click.Path(), 
              help='Output file path')
@click.option('--include-dev', is_flag=True,
              help='Include development dependencies')
@click.option('--show-dependents', is_flag=True,
              help='Show what packages depend on each dependency')
@click.option('--json-output', is_flag=True,
              help='Output results in JSON format')
def detect(output_format: str, 
           output: Optional[str],
           include_dev: bool,
           show_dependents: bool,
           json_output: bool):
    """Detect and list primary dependencies (packages YOU installed)."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing dependencies...", total=None)

        try:
            from .core.detector import DependencyDetector
            detector = DependencyDetector()

            # Get primary packages
            primary_packages = detector.detect_primary_packages()

            if json_output:
                result = {
                    'primary_packages': primary_packages,
                    'total_count': len(primary_packages),
                    'environment_type': detector.env_type
                }
                console.print_json(json.dumps(result, indent=2))
                return

            if output:
                # Generate requirements file
                with open(output, 'w') as f:
                    f.write("# Primary dependencies detected by pywise_pkg\n\n")
                    for pkg in primary_packages:
                        version = f"=={pkg['version']}" if pkg.get('version') else ''
                        f.write(f"{pkg['name']}{version}\n")

                console.print(f"[green]✓ Requirements written to {output}[/green]")
                return

            # Console output
            if not primary_packages:
                console.print("[yellow]No primary packages detected.[/yellow]")
                return

            table = Table(title=f"Primary Dependencies ({len(primary_packages)} found)")
            table.add_column("Package", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Source", style="blue")

            if show_dependents:
                table.add_column("Dependents", style="yellow")

            for pkg in sorted(primary_packages, key=lambda x: x['name']):
                row = [
                    pkg['name'],
                    pkg.get('version', 'unknown'),
                    pkg.get('source', 'unknown')
                ]

                if show_dependents:
                    dependents = pkg.get('dependents', [])
                    dependents_str = ', '.join(dependents[:3])
                    if len(dependents) > 3:
                        dependents_str += f" (+{len(dependents)-3} more)"
                    row.append(dependents_str or "none")

                table.add_row(*row)

            console.print(table)
            console.print(f"\n[dim]Environment: {detector.env_type}[/dim]")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

@cli.command()
@click.argument('packages', nargs=-1)
@click.option('--strategy', default='hybrid',
              type=click.Choice(['hybrid', 'conda-only', 'pip-only']),
              help='Resolution strategy')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for resolved dependencies')
def resolve(packages: List[str], strategy: str, output: Optional[str]):
    """Resolve dependencies with conda-pip hybrid intelligence."""

    if not packages:
        console.print("[red]Please specify packages to resolve[/red]")
        console.print("Example: pywise_pkg resolve numpy pandas tensorflow")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Resolving with hybrid approach...", total=None)

        try:
            from .core.resolver import HybridDependencyResolver
            resolver = HybridDependencyResolver()

            # Analyze packages
            analysis = resolver.analyze_package_sources(packages)

            # Show analysis
            console.print("\n[bold]Package Source Analysis:[/bold]")

            if analysis['conda_packages']:
                table = Table(title="Recommended for Conda")
                table.add_column("Package", style="green")
                table.add_column("Reason", style="dim")

                for pkg in analysis['conda_packages']:
                    table.add_row(pkg['original'], pkg['reason'])
                console.print(table)

            if analysis['pip_packages']:
                table = Table(title="Recommended for Pip")
                table.add_column("Package", style="cyan")
                table.add_column("Reason", style="dim")

                for pkg in analysis['pip_packages']:
                    table.add_row(pkg['original'], pkg['reason'])
                console.print(table)

            if analysis['recommendations']:
                console.print("\n[bold]Recommendations:[/bold]")
                for rec in analysis['recommendations']:
                    console.print(f"  • {rec}")

            # Generate hybrid solution
            if strategy == 'hybrid':
                result = resolver.resolve_hybrid_environment(packages, 'conda')

                if result['success']:
                    console.print(f"\n[green]✓ Hybrid solution ready![/green]")
                    console.print(f"  Conda packages: {result['conda_packages']}")
                    console.print(f"  Pip packages: {result['pip_packages']}")

                    if output:
                        import yaml
                        with open(output, 'w') as f:
                            yaml.dump(result['config'], f, default_flow_style=False)
                        console.print(f"  Output written to: {output}")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

@cli.command('venv-to-conda')
@click.option('--name', '-n', help='Name for the new conda environment')
@click.option('--python-version', help='Python version for conda environment')
@click.option('--keep-venv', is_flag=True, help='Keep original virtual environment')
def venv_to_conda(name: Optional[str], python_version: Optional[str], keep_venv: bool):
    """Convert current venv to conda environment - SINGLE COMMAND!"""

    console.print("[bold blue]🔄 Converting venv to conda environment...[/bold blue]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Converting environment...", total=None)

        try:
            from .core.migrator import AdvancedEnvironmentMigrator
            migrator = AdvancedEnvironmentMigrator()

            result = migrator.convert_venv_to_conda(
                env_name=name,
                python_version=python_version,
                keep_venv=keep_venv
            )

            if result['success']:
                console.print(f"\n[green]✅ Conversion successful![/green]")

                # Show summary
                summary_table = Table(title="Conversion Summary")
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="green")

                summary_table.add_row("New Environment", result['new_env_name'])
                summary_table.add_row("Conda Packages", str(result['conda_packages']))
                summary_table.add_row("Pip Packages", str(result['pip_packages']))
                summary_table.add_row("Files Created", ', '.join(result['files_created']))

                console.print(summary_table)

                # Show next steps
                console.print("\n[bold]Next Steps:[/bold]")
                for step in result['next_steps']:
                    console.print(f"  1. {step}")

                # Show activation command prominently
                activation_panel = Panel(
                    f"conda activate {result['new_env_name']}",
                    title="🚀 Activate Your New Environment",
                    border_style="green"
                )
                console.print(activation_panel)

            else:
                console.print(f"[red]❌ Conversion failed: {result['error']}[/red]")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

@cli.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.option('--to', 'target_format', required=True,
              type=click.Choice(['pip', 'conda', 'poetry', 'pipenv']),
              help='Target format')
@click.option('--output', '-o', type=click.Path(),
              help='Output file path')
def migrate(source_file: str, target_format: str, output: Optional[str]):
    """Migrate between dependency formats - SINGLE COMMAND!"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Migrating formats...", total=None)

        try:
            from .core.migrator import AdvancedEnvironmentMigrator
            migrator = AdvancedEnvironmentMigrator()

            result = migrator.migrate_between_formats(
                source_file=source_file,
                target_format=target_format,
                output_file=output
            )

            if result['success']:
                console.print(f"[green]✅ Migration successful![/green]")
                console.print(f"  Source: {result['source_file']} ({result['source_format']})")
                console.print(f"  Target: {result['output_file']} ({result['target_format']})")
                console.print(f"  Packages: {result['packages_converted']}")
            else:
                console.print(f"[red]❌ Migration failed: {result['error']}[/red]")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

@cli.command()
@click.option('--python-version', default='3.11', help='Python version')
@click.option('--optimize', is_flag=True, default=True, help='Optimize Docker build')
@click.option('--build', is_flag=True, help='Build Docker image after generation')
@click.option('--tag', help='Docker image tag (required with --build)')
def dockerize(python_version: str, optimize: bool, build: bool, tag: Optional[str]):
    """Generate optimized Docker configuration - SINGLE COMMAND!"""

    if build and not tag:
        console.print("[red]--tag is required when using --build[/red]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating Docker configuration...", total=None)

        try:
            from .core.docker_gen import DockerGenerator
            docker_gen = DockerGenerator()

            result = docker_gen.dockerize_project(
                python_version=python_version,
                optimize=optimize,
                build=build,
                tag=tag
            )

            if result['success']:
                console.print(f"[green]✅ Docker files generated![/green]")

                # Show files created
                for file_path in result['files_created']:
                    console.print(f"  Created: {file_path}")

                # Show analysis
                analysis = result['analysis']

                info_panel = Panel.fit(
                    f"Estimated Size: {analysis['estimated_size_mb']} MB\n"
                    f"System Dependencies: {len(analysis['system_deps'])}\n"
                    f"Project Type: {analysis.get('is_ml', False) and 'ML' or 'Web' if analysis.get('web_framework') else 'General'}",
                    title="📊 Docker Image Info",
                    border_style="blue"
                )
                console.print(info_panel)

                if 'build_result' in result and result['build_result']['success']:
                    console.print(f"\n[green]✅ Docker image '{tag}' built successfully![/green]")

            else:
                console.print(f"[red]❌ Docker generation failed: {result['error']}[/red]")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

@cli.command('multi-env')
@click.option('--environments', '-e', multiple=True, 
              default=['dev', 'staging', 'prod'],
              help='Environment names to create')
def multi_env(environments: List[str]):
    """Setup multi-environment configuration (dev/staging/prod) - SINGLE COMMAND!"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Setting up multi-environment...", total=None)

        try:
            from .core.migrator import AdvancedEnvironmentMigrator
            migrator = AdvancedEnvironmentMigrator()

            result = migrator.setup_multi_environment(list(environments))

            if result['success']:
                console.print(f"[green]✅ Multi-environment setup complete![/green]")

                # Show created files
                table = Table(title="Files Created")
                table.add_column("File", style="cyan")
                table.add_column("Purpose", style="dim")

                for file_path in result['files_created']:
                    if 'requirements-' in file_path:
                        env_name = file_path.split('requirements-')[1].split('.')[0]
                        table.add_row(file_path, f"{env_name.title()} environment dependencies")
                    else:
                        table.add_row(file_path, "Multi-environment configuration")

                console.print(table)

                # Show usage
                usage_panel = Panel(
                    f"Files created for environments: {', '.join(result['environments'])}\n"
                    f"Main config: {result['config_file']}",
                    title="🎯 Multi-Environment Ready",
                    border_style="green"
                )
                console.print(usage_panel)

            else:
                console.print(f"[red]❌ Setup failed: {result['error']}[/red]")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

@cli.command()
@click.option('--unused', is_flag=True, help='Show unused packages')
@click.option('--missing', is_flag=True, help='Show missing packages for imports')
@click.option('--full', is_flag=True, help='Show full analysis')
def analyze(unused: bool, missing: bool, full: bool):
    """Analyze imports vs installed packages."""

    if not any([unused, missing, full]):
        full = True

    console.print("[yellow]Analysis functionality coming in next version![/yellow]")
    console.print("This will detect unused packages and missing imports.")

def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()
