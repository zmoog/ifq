import datetime
from pathlib import Path

import click

from ifq import Scraper


@click.group()
@click.version_option()
@click.option(
    "--username",
    required=True,
    envvar="IFQ_USERNAME",
)
@click.option(
    "--password",
    required=True,
    envvar="IFQ_PASSWORD",
)
@click.pass_context
def cli(ctx: click.Context, username: str, password: str):
    "CLI tool and Python library to download PDF issues of ilfattoquotidiano.it"
    ctx.ensure_object(dict)
    ctx.obj = {
        "username": username,
        "password": password,
    }


@cli.group(name="issues")
def issues():
    "Issues related commands"
    pass


@issues.command(name="download")
@click.argument(
    # https://click.palletsprojects.com/en/stable/arguments/
    "pub_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(file_okay=False, writable=True, resolve_path=True),
    help="Output directory",
    default=Path.cwd(),
)
@click.pass_context
def download(ctx: click.Context, pub_date: datetime.date, output_dir: Path):
    "Download issue as PDF file"
    click.echo(f"Downloading issue for {pub_date} to {output_dir}")

    try:
        scraper = Scraper(ctx.obj["username"], ctx.obj["password"])
        file = scraper.download_pdf(pub_date, output_dir)
    except Exception as e:
        raise click.ClickException(f"failed to download issue: {e}")

    click.echo(f"Downloaded issue to {file}")
