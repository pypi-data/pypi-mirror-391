import asyncio
import click

from fediverse_pasture.runner.config import SendingConfig

from . import handle_send_to
from .modifier import ModifierBuilder


@click.command()
@click.option(
    "--domain",
    default="http://pasture-one-actor",
    help="Domain the actor is served one",
)
@click.option("--text", help="Content of the message to be send")
@click.option("--input_name", help="Name of the fediverse-pasture-input to use")
@click.option("--input_number", type=int, help="Id of the input to use")
@click.option(
    "--mention", is_flag=True, default=False, help="triggers mentioning the user"
)
@click.option(
    "--include_cc",
    is_flag=True,
    default=False,
    help="ensures that the cc property is set on activity and object",
)
@click.option(
    "--replace_https", is_flag=True, default=False, help="replace https:// with http://"
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="if true prints the resulting activity",
)
@click.argument("uri")
def send_to(
    domain,
    text,
    uri,
    input_name: str,
    input_number: int,
    mention: bool,
    include_cc: bool,
    replace_https: bool,
    verbose: bool,
):
    modifier = ModifierBuilder(
        text=text, input_name=input_name, input_number=input_number
    ).build()

    sending_config = SendingConfig(include_cc=include_cc, include_mention=mention)

    if not asyncio.run(
        handle_send_to(modifier, domain, uri, sending_config, replace_https, verbose)
    ):
        exit(1)

    if verbose:
        print("Activity send successfully`")


if __name__ == "__main__":
    send_to()
