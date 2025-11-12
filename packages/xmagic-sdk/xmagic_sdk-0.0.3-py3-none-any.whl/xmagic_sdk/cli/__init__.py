import click

from xmagic_sdk.__about__ import __version__
from xmagic_sdk.cli.configure import configure_command
from xmagic_sdk.cli.chat import chat_command
from xmagic_sdk.cli.mcp import mcp_command


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="xMagic")
@click.pass_context
def xmagic(ctx: click.Context):
    pass


xmagic.add_command(configure_command)
xmagic.add_command(chat_command)
xmagic.add_command(mcp_command)
