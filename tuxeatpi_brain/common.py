"""Module customizing the cli"""
import click

from tuxeatpi_brain.daemon import Brain
from tuxeatpi_common.cli import cli, main_cli


CONFIG_OPTION = click.core.Option(['--config-file', '-c'],
                                  required=True,
                                  help="Config file",
                                  expose_value=True,
                                  type=click.Path(exists=True,
                                                  file_okay=True,
                                                  dir_okay=False,
                                                  writable=True,
                                                  readable=True))

main_cli.params.append(CONFIG_OPTION)


cli(Brain)
