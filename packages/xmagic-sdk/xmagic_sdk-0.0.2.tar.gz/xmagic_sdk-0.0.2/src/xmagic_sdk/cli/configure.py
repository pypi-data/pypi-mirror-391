import click
from typing import Optional

from xmagic_sdk.utils.config_utils import overwrite_config
from xmagic_sdk.utils.validations import is_config_valid


@click.command(name="configure")
@click.option("-k", "--api_key", hide_input=False, prompt="[*] Your API key")
def configure_command(api_key: Optional[str]):
    """Configure your XChat CLI with the necessary API key."""

    xchat_config = {
        "XCHAT_API_KEY": api_key,
    }

    click.secho("[*] Validating your data...", fg="white", bold=True)
    is_valid = is_config_valid(api_key=api_key)
    if not is_valid:
        return click.secho(
            "[!] Your configuration is not valid. Make sure to provide the correct API Key. If the problem persists contact support.",
            fg="red",
            bold=True,
        )

    overwrite_config(xchat_config)
    click.secho("[+] Configuration added successfully", fg="green", bold=True)
