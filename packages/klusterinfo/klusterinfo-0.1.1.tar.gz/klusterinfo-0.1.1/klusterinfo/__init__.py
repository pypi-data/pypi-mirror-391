import click

from .api import NodeInformation


@click.command()
def cli():
    n = NodeInformation()
    n.get_nodes()


if __name__ == "__main__":
    cli()
