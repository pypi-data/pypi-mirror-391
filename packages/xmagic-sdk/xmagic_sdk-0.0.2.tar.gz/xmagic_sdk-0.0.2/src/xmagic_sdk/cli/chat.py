import click
from typing import Optional

from xmagic_sdk.chatting.chatting import chat, create_new_chat
from xmagic_sdk.utils.config_utils import get_api_key


@click.command(name="chat")
@click.option("-a", "--agent_id", required=True, help="The persona ID or chatbot ID")
@click.option("-j", "--job_id", default=None, help="Optional job ID for routing")
@click.option("--voice", is_flag=True, help="Simulate voice interaction")
@click.option(
    "--chat-type", default="playground", help="Chat type (default: playground)"
)
def chat_command(
    agent_id: str,
    job_id: Optional[str],
    voice: bool,
    chat_type: str,
):
    """Start an interactive chat session with a persona or chatbot."""

    try:
        api_key = get_api_key()

        if not api_key:
            click.secho(
                "[!] API key not found. Please configure your API key using the 'xmagic configure' command.",
                fg="red",
                bold=True,
            )
            return

        if chat_type not in ["playground", "interact"]:
            click.secho(
                f"Error: Invalid chat type '{chat_type}'. Must be 'playground' or 'interact'.",
                fg="red",
                bold=True,
            )
            return

        # Create a new chat session
        chat_id = create_new_chat(
            agent_id=agent_id,
            title="CLI Chat Session",
            chat_type=chat_type,
        )

        click.secho(f"✓ Created chat session: {chat_id}", fg="green", bold=True)
        click.echo(f"Chat Type: {chat_type}")
        click.secho("Type your messages below. Press Ctrl+C to exit.\n", fg="cyan")

        while True:
            query = input("\033[94m\n\nEnter your query: \033[0m")

            if not query.strip():
                continue

            # Send the query and stream the response
            chat(
                agent_id=agent_id,
                chat_id=chat_id,
                query=query,
                job_id=job_id,
                simulate_voice=voice,
                stream=True,
            )

    except KeyboardInterrupt:
        click.secho("\n\nChat session ended.", fg="yellow")
    except Exception as e:
        click.secho(f"\n\nError: {str(e)}", fg="red", bold=True)
