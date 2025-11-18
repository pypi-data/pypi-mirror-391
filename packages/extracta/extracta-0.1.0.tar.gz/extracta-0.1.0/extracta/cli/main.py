import click
from pathlib import Path
from extracta.lenses import get_lens_for_file
from extracta.analyzers import get_analyzer_for_content


@click.group()
@click.version_option()
def main():
    """Extracta - Modular content analysis and insight generation"""
    pass


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--mode", type=click.Choice(["research", "assessment"]), default="assessment"
)
@click.option("--output", "-o", type=click.Path())
def analyze(file_path, mode, output):
    """Analyze content from file"""
    file_path = Path(file_path)

    # Get appropriate lens
    lens = get_lens_for_file(file_path)
    if not lens:
        click.echo(f"No lens available for {file_path.suffix}", err=True)
        return

    click.echo(f"Analyzing {file_path.name}...")

    # Extract content
    result = lens.extract(file_path)
    if not result.success:
        click.echo(f"Error: {result.error}", err=True)
        return

    # Analyze content
    analyzer = get_analyzer_for_content(result.data["content_type"])
    if analyzer:
        analysis = analyzer.analyze(result.data["raw_content"], mode)
        result.data["analysis"] = analysis

    # Output results
    if output:
        import json

        with open(output, "w") as f:
            json.dump(result.data, f, indent=2)
    else:
        click.echo(json.dumps(result.data, indent=2))
