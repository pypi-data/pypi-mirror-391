import asyncio
import sys
from typing import Optional
import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from . import __version__
from .config import get_config_manager, Config, APIProvider
from .client import create_client
from .display import DisplayManager, LiveWorkflowDisplay
from .session import SessionManager, ConversationSession
from .models import Message
from .logger import init_debug_logger, get_debug_logger

# Jarvis environment URLs
JARVIS_ENV_URLS = {
    "local": "http://localhost:7961/api/v1",
    "beta": "https://jvs-api.atomecorp.net/api/v1",
    "prod": "https://jarvis-api.atomecorp.net/api/v1",
}


app = typer.Typer(
    name="jvs-cli",
    help="Terminal-based AI chat interface with support for Jarvis, OpenAI, and Claude",
    add_completion=False,
    invoke_without_command=True,
    no_args_is_help=False,
)


# Main callback - runs when no command is provided
@app.callback()
def main(
    ctx: typer.Context,
    conversation_id: Optional[str] = typer.Option(
        None, "--conversation", "-c", help="Continue existing conversation"
    ),
    openai: bool = typer.Option(
        False, "-openai", help="Use OpenAI API"
    ),
    claude: bool = typer.Option(
        False, "-claude", help="Use Claude API"
    ),
    local: bool = typer.Option(
        False, "-local", help="Use local Jarvis environment (localhost:7961)"
    ),
    beta: bool = typer.Option(
        False, "-beta", help="Use beta Jarvis environment"
    ),
    prod: bool = typer.Option(
        False, "-prod", help="Use production Jarvis environment"
    ),
    key: Optional[str] = typer.Option(
        None, "-k", "--key", help="API key for OpenAI or Claude"
    ),
    live: bool = typer.Option(
        False, "--live", "-l", help="Enable live workflow display mode"
    ),
    theme: str = typer.Option(
        "claude_dark", "--theme", "-t", help="Color theme (claude_dark, github_dark, monokai, dracula, nord)"
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debug logging to ./logs directory"
    ),
    version: bool = typer.Option(
        None, "--version", "-v", help="Show version and exit"
    ),
    editor: bool = typer.Option(
        False, "--editor", "-e", help="Enable editor mode for document editing"
    )
) -> None:
    if version:
        typer.echo(f"jvs-cli version {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is not None:
        return

    # Determine API provider and environment
    provider = APIProvider.JARVIS
    jarvis_env = None
    jarvis_url = None

    if openai:
        provider = APIProvider.OPENAI
    elif claude:
        provider = APIProvider.CLAUDE
    elif local:
        provider = APIProvider.JARVIS
        jarvis_env = "local"
        jarvis_url = JARVIS_ENV_URLS["local"]
    elif beta:
        provider = APIProvider.JARVIS
        jarvis_env = "beta"
        jarvis_url = JARVIS_ENV_URLS["beta"]
    elif prod:
        provider = APIProvider.JARVIS
        jarvis_env = "prod"
        jarvis_url = JARVIS_ENV_URLS["prod"]

    ctx.ensure_object(dict)
    ctx.obj["live_mode"] = live
    ctx.obj["theme"] = theme
    ctx.obj["debug"] = debug
    ctx.obj["provider"] = provider
    ctx.obj["api_key"] = key
    ctx.obj["jarvis_env"] = jarvis_env
    ctx.obj["jarvis_url"] = jarvis_url
    ctx.obj["editor"] = editor
    asyncio.run(_run_interactive_mode(
        conversation_id,
        provider=provider,
        api_key=key,
        jarvis_env=jarvis_env,
        jarvis_url=jarvis_url,
        live_mode=live,
        theme=theme,
        debug=debug,
        editor_mode=editor
    ))


# One-shot query mode
@app.command()
def ask(
    query: str = typer.Argument(..., help="Question to ask"),
    conversation_id: Optional[str] = typer.Option(
        None, "--conversation", "-c", help="Continue existing conversation"
    ),
    openai: bool = typer.Option(
        False, "-openai", help="Use OpenAI API"
    ),
    claude: bool = typer.Option(
        False, "-claude", help="Use Claude API"
    ),
    local: bool = typer.Option(
        False, "-local", help="Use local Jarvis environment"
    ),
    beta: bool = typer.Option(
        False, "-beta", help="Use beta Jarvis environment"
    ),
    prod: bool = typer.Option(
        False, "-prod", help="Use production Jarvis environment"
    ),
    key: Optional[str] = typer.Option(
        None, "-k", "--key", help="API key for OpenAI or Claude"
    ),
    live: bool = typer.Option(
        False, "--live", "-l", help="Enable live workflow display mode"
    ),
    theme: str = typer.Option(
        "claude_dark", "--theme", "-t", help="Color theme"
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debug logging to ./logs directory"
    ),
) -> None:
    # Determine API provider and environment
    provider = APIProvider.JARVIS
    jarvis_env = None
    jarvis_url = None

    if openai:
        provider = APIProvider.OPENAI
    elif claude:
        provider = APIProvider.CLAUDE
    elif local:
        provider = APIProvider.JARVIS
        jarvis_env = "local"
        jarvis_url = JARVIS_ENV_URLS["local"]
    elif beta:
        provider = APIProvider.JARVIS
        jarvis_env = "beta"
        jarvis_url = JARVIS_ENV_URLS["beta"]
    elif prod:
        provider = APIProvider.JARVIS
        jarvis_env = "prod"
        jarvis_url = JARVIS_ENV_URLS["prod"]

    asyncio.run(_run_one_shot(
        query,
        conversation_id,
        provider=provider,
        api_key=key,
        jarvis_env=jarvis_env,
        jarvis_url=jarvis_url,
        live_mode=live,
        theme=theme,
        debug=debug
    ))


# Chat command (alias for main with conversation)
@app.command()
def chat(
    conversation_id: Optional[str] = typer.Argument(
        None, help="Conversation ID to continue"
    ),
    openai: bool = typer.Option(
        False, "-openai", help="Use OpenAI API"
    ),
    claude: bool = typer.Option(
        False, "-claude", help="Use Claude API"
    ),
    local: bool = typer.Option(
        False, "-local", help="Use local Jarvis environment"
    ),
    beta: bool = typer.Option(
        False, "-beta", help="Use beta Jarvis environment"
    ),
    prod: bool = typer.Option(
        False, "-prod", help="Use production Jarvis environment"
    ),
    key: Optional[str] = typer.Option(
        None, "-k", "--key", help="API key for OpenAI or Claude"
    ),
    live: bool = typer.Option(
        False, "--live", "-l", help="Enable live workflow display mode"
    ),
    theme: str = typer.Option(
        "claude_dark", "--theme", "-t", help="Color theme"
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debug logging to ./logs directory"
    ),
) -> None:
    # Determine API provider and environment
    provider = APIProvider.JARVIS
    jarvis_env = None
    jarvis_url = None

    if openai:
        provider = APIProvider.OPENAI
    elif claude:
        provider = APIProvider.CLAUDE
    elif local:
        provider = APIProvider.JARVIS
        jarvis_env = "local"
        jarvis_url = JARVIS_ENV_URLS["local"]
    elif beta:
        provider = APIProvider.JARVIS
        jarvis_env = "beta"
        jarvis_url = JARVIS_ENV_URLS["beta"]
    elif prod:
        provider = APIProvider.JARVIS
        jarvis_env = "prod"
        jarvis_url = JARVIS_ENV_URLS["prod"]

    asyncio.run(_run_interactive_mode(
        conversation_id,
        provider=provider,
        api_key=key,
        jarvis_env=jarvis_env,
        jarvis_url=jarvis_url,
        live_mode=live,
        theme=theme,
        debug=debug
    ))


# Configuration commands
config_app = typer.Typer(help="Configuration management")
app.add_typer(config_app, name="config")


@config_app.command("init")
def config_init() -> None:
    config_manager = get_config_manager()
    if config_manager.exists():
        typer.confirm("Configuration already exists. Overwrite?", abort=True)
    config_manager.init_interactive()


@config_app.command("show")
def config_show() -> None:
    config_manager = get_config_manager()
    if not config_manager.exists():
        typer.echo("No configuration found. Run 'jvs-cli config init' first.")
        raise typer.Exit(1)
    config = config_manager.get()
    display = DisplayManager()
    display.console.print("[bold cyan]Current Configuration:[/bold cyan]\n")
    display.console.print(f"[yellow]Current Provider:[/yellow] {config.api_provider.value}\n")

    # Show provider-specific config
    if config.api_provider == APIProvider.JARVIS:
        display.console.print("[bold cyan]Jarvis Configuration:[/bold cyan]")
        display.console.print(f"[yellow]API Base URL:[/yellow] {config.jarvis.api_base_url}")
        display.console.print(f"[yellow]Login Code:[/yellow] {config.jarvis.login_code or config.jarvis.user_id}")
    elif config.api_provider == APIProvider.OPENAI:
        display.console.print("[bold cyan]OpenAI Configuration:[/bold cyan]")
        display.console.print(f"[yellow]API Key:[/yellow] {'***' + config.openai.api_key[-4:] if config.openai.api_key else 'Not set'}")
        display.console.print(f"[yellow]Model:[/yellow] {config.openai.model}")
    elif config.api_provider == APIProvider.CLAUDE:
        display.console.print("[bold cyan]Claude Configuration:[/bold cyan]")
        display.console.print(f"[yellow]API Key:[/yellow] {'***' + config.claude.api_key[-4:] if config.claude.api_key else 'Not set'}")
        display.console.print(f"[yellow]Model:[/yellow] {config.claude.model}")

    display.console.print(f"\n[bold cyan]Display Settings:[/bold cyan]")
    display.console.print(f"[yellow]Theme:[/yellow] {config.display.theme}")
    display.console.print(f"[yellow]Live Mode:[/yellow] {config.display.live_mode}")
    display.console.print(f"\n[dim]Config file: {config_manager.config_path}[/dim]")


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key (e.g., 'user_id')"),
    value: str = typer.Argument(..., help="New value"),
) -> None:
    config_manager = get_config_manager()
    if not config_manager.exists():
        typer.echo("No configuration found. Run 'jvs-cli config init' first.")
        raise typer.Exit(1)
    try:
        config_manager.set_value(key, value)
        typer.echo(f"Set {key} = {value}")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


# Login command
@app.command()
def login(
    local: bool = typer.Option(False, "-local", help="Login to local environment"),
    beta: bool = typer.Option(False, "-beta", help="Login to beta environment"),
    prod: bool = typer.Option(False, "-prod", help="Login to production environment"),
) -> None:
    """Authenticate with Jarvis using OAuth flow"""
    from rich.console import Console
    from .login import login as do_login, extract_user_info, LoginError

    console = Console()
    config_manager = get_config_manager()
    config = config_manager.get()

    # Determine environment
    jarvis_env = None
    jarvis_url = None

    if local:
        jarvis_env = "local"
        jarvis_url = JARVIS_ENV_URLS["local"]
    elif beta:
        jarvis_env = "beta"
        jarvis_url = JARVIS_ENV_URLS["beta"]
    elif prod:
        jarvis_env = "prod"
        jarvis_url = JARVIS_ENV_URLS["prod"]

    # Display environment info
    if jarvis_env:
        console.print(f"\n[cyan]Logging in to {jarvis_env} environment[/cyan]")
        console.print(f"[dim]URL: {jarvis_url}[/dim]\n")
        config.jarvis.api_base_url = jarvis_url
    elif config.jarvis.api_base_url:
        console.print(f"\n[cyan]Logging in to: {config.jarvis.api_base_url}[/cyan]\n")
    else:
        console.print("\n[cyan]Logging in to Jarvis[/cyan]\n")

    try:
        # Perform OAuth login
        jwt_token, expires_at = asyncio.run(do_login(console=console))

        # Extract user info from token
        user_info = extract_user_info(jwt_token)

        # Save token to config
        config.jarvis.jwt_token = jwt_token
        config.jarvis.token_expires_at = expires_at.isoformat()

        # Also update user_id from token if available
        if user_info.get("user_id"):
            config.jarvis.user_id = user_info["user_id"]

        config_manager.save(config)

        # Display success message with user info
        console.print("\n[green]✓ Login successful![/green]\n")

        if user_info.get("name"):
            console.print(f"[yellow]Name:[/yellow] {user_info['name']}")
        if user_info.get("email"):
            console.print(f"[yellow]Email:[/yellow] {user_info['email']}")
        if user_info.get("user_id"):
            console.print(f"[yellow]User ID:[/yellow] {user_info['user_id']}")

        console.print(f"\n[dim]Token expires at: {expires_at.strftime('%Y-%m-%d %H:%M:%S %Z')}[/dim]")
        console.print(f"[dim]Config saved to: {config_manager.config_path}[/dim]\n")

    except LoginError as e:
        console.print(f"\n[red]✗ Login failed:[/red] {e}\n")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Login cancelled by user[/yellow]\n")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"\n[red]✗ Unexpected error:[/red] {e}\n")
        raise typer.Exit(1)


# History command
@app.command()
def history(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of conversations to show")
) -> None:
    session_manager = SessionManager()
    sessions = session_manager.list_sessions(limit=limit)
    display = DisplayManager()
    if not sessions:
        display.print_info("No conversation history found.")
        return
    display.console.print("[bold cyan]Recent Conversations:[/bold cyan]\n")
    for session in sessions:
        conv_id = session.get("conversation_id", "unknown")
        updated = session.get("updated_at", "unknown")
        msg_count = session.get("message_count", 0)
        display.console.print(
            f"[yellow]{conv_id}[/yellow] - "
            f"[dim]{updated}[/dim] - "
            f"{msg_count} messages"
        )


# Internal helper functions
async def _run_interactive_mode(
    conversation_id: Optional[str] = None,
    provider: APIProvider = APIProvider.JARVIS,
    api_key: Optional[str] = None,
    jarvis_env: Optional[str] = None,
    jarvis_url: Optional[str] = None,
    live_mode: bool = False,
    theme: str = "claude_dark",
    debug: bool = False,
    editor_mode: bool = False
) -> None:
    debug_logger = init_debug_logger(enabled=debug)
    if debug:
        typer.echo(f"[DEBUG] Logging enabled. Logs will be saved to: {debug_logger.log_file}")

    config_manager = get_config_manager()
    config = config_manager.get()

    # Handle API key for external providers
    if provider in [APIProvider.OPENAI, APIProvider.CLAUDE]:
        if api_key:
            # Save the API key for future use
            if provider == APIProvider.OPENAI:
                config.openai.api_key = api_key
            else:
                config.claude.api_key = api_key
            config.api_provider = provider
            config_manager.save(config)
            typer.echo(f"API key saved for {provider.value}")
        else:
            # Try to use saved key
            if provider == APIProvider.OPENAI:
                api_key = config.openai.api_key
            else:
                api_key = config.claude.api_key

            if not api_key:
                typer.echo(f"Error: API key required for {provider.value}. Use -k option to provide it.")
                raise typer.Exit(1)

    # Check Jarvis config if using Jarvis
    elif provider == APIProvider.JARVIS:
        if jarvis_env:
            # Using predefined environment, override URL
            config.jarvis.api_base_url = jarvis_url
            if jarvis_env == "local":
                typer.echo(f"Using local Jarvis environment: {jarvis_url}")
            else:
                typer.echo(f"Using {jarvis_env} Jarvis environment: {jarvis_url}")

            # Check if login_code is set, if not prompt for it
            if not config.jarvis.login_code and not config.jarvis.user_id:
                from rich.prompt import Prompt
                login_code = Prompt.ask("Login Code").strip()
                config.jarvis.login_code = login_code
                config_manager.save(config)
        else:
            # Using configured Jarvis
            if not config_manager.exists() or not config.jarvis.api_base_url:
                typer.echo("No Jarvis configuration found. Running setup wizard...\n")
                config_manager.init_interactive()
                config = config_manager.get()

    final_live_mode = live_mode or config.display.live_mode
    final_theme = theme if theme != "claude_dark" else config.display.theme
    if final_live_mode:
        display = LiveWorkflowDisplay(config=config.display, theme_name=final_theme)
    else:
        display = DisplayManager(config=config.display)

    session_manager = SessionManager()
    if conversation_id:
        try:
            session = session_manager.load_session(conversation_id)
            display.print_info(f"Continuing conversation: {conversation_id}")
        except FileNotFoundError:
            display.print_error(f"Conversation not found: {conversation_id}")
            session = session_manager.new_session()
    else:
        session = session_manager.new_session()

    # Handle editor mode initialization
    editor_doc_data = None
    editor_doc_url = None
    editor_doc_name = None
    if editor_mode:
        from rich.prompt import Prompt
        from rich.panel import Panel
        from .client import extract_doc_id_from_url, fetch_lark_document
        import json

        display.console.print(Panel.fit(
            "[cyan]Editor Mode[/cyan]\n"
            "Please provide a Lark document URL to edit.",
            border_style="cyan"
        ))

        doc_url = Prompt.ask("Document URL").strip()
        doc_id = extract_doc_id_from_url(doc_url)

        if not doc_id:
            display.print_error("Invalid Lark document URL")
            raise typer.Exit(1)

        display.console.print("[yellow]Loading document...[/yellow]")

        try:
            editor_doc_data = await fetch_lark_document(doc_id)
            editor_doc_url = doc_url
            # Extract document name from nodes (first page node)
            nodes = editor_doc_data.get("nodes", [])
            editor_doc_name = "Unknown Document"
            if nodes and nodes[0].get("type") == "page":
                editor_doc_name = nodes[0].get("title", "Unknown Document")

            # Store editor mode info in session
            session.editor_mode = True
            session.document_url = editor_doc_url
            session.document_name = editor_doc_name

            # Display document status header
            display.console.print(Panel(
                f"[green]current_document:[/green] {editor_doc_name}\n"
                f"[green]url:[/green] {editor_doc_url}\n"
                f"[green]status:[/green] success loaded",
                title="[bold cyan]Editor Mode[/bold cyan]",
                border_style="green"
            ))
            display.console.print()
        except Exception as e:
            display.print_error(f"Failed to load document: {e}")
            raise typer.Exit(1)

    # Define token refresh callback
    def on_token_refresh(new_token: str, new_expires_at: str):
        """Callback to save refreshed token to config"""
        config.jarvis.jwt_token = new_token
        config.jarvis.token_expires_at = new_expires_at
        config_manager.save(config)

    # Create the appropriate client
    if provider == APIProvider.JARVIS:
        client = create_client(
            provider=provider,
            config={
                "base_url": config.jarvis.api_base_url,
                "user_id": config.jarvis.effective_user_id,
                "jwt_token": config.jarvis.jwt_token,
                "token_expires_at": config.jarvis.token_expires_at,
                "on_token_refresh": on_token_refresh,
            }
        )
    elif provider == APIProvider.OPENAI:
        client = create_client(
            provider=provider,
            config={
                "api_key": api_key,
                "model": config.openai.model,
            }
        )
    else:  # Claude
        client = create_client(
            provider=provider,
            config={
                "api_key": api_key,
                "model": config.claude.model,
            }
        )
    display.print_welcome()
    prompt_session = PromptSession(history=InMemoryHistory())

    try:
        while True:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: prompt_session.prompt("You: ")
                )
            except (EOFError, KeyboardInterrupt):
                break
            user_input = user_input.strip()
            if not user_input:
                continue
            
            # Handle exit command (with or without /)
            if user_input == "exit" or user_input == "/exit" or user_input == "quit":
                break
                
            if user_input.startswith("/"):
                if user_input == "/new":
                    session = session_manager.new_session()
                    display.print_info("Started new conversation")
                    continue
                elif user_input == "/help":
                    display.print_help()
                    continue
                elif user_input == "/history":
                    sessions = session_manager.list_sessions()
                    if sessions:
                        display.console.print("\n[bold cyan]Recent Conversations:[/bold cyan]\n")
                        for s in sessions[:5]:
                            display.console.print(
                                f"[yellow]{s.get('conversation_id', 'unknown')}[/yellow] - "
                                f"[dim]{s.get('updated_at', 'unknown')}[/dim]"
                            )
                        display.console.print()
                    else:
                        display.print_info("No conversation history")
                    continue
                elif user_input == "/config":
                    display.console.print(f"\n[yellow]Provider:[/yellow] {provider.value}")
                    if provider == APIProvider.JARVIS:
                        display.console.print(f"[yellow]API:[/yellow] {config.jarvis.api_base_url}")
                        display.console.print(f"[yellow]Login:[/yellow] {config.jarvis.effective_user_id}")
                    elif provider == APIProvider.OPENAI:
                        display.console.print(f"[yellow]API Key:[/yellow] {'***' + api_key[-4:] if api_key else 'Not set'}")
                        display.console.print(f"[yellow]Model:[/yellow] {config.openai.model}")
                    else:  # Claude
                        display.console.print(f"[yellow]API Key:[/yellow] {'***' + api_key[-4:] if api_key else 'Not set'}")
                        display.console.print(f"[yellow]Model:[/yellow] {config.claude.model}")
                    display.console.print()
                    continue
                else:
                    display.print_error(f"Unknown command: {user_input}")
                    continue
            # Prepare user input - add document context for first message in editor mode
            final_user_input = user_input
            if editor_mode and editor_doc_data and len(session.get_messages()) == 0:
                import json
                doc_json = json.dumps({"code": 0, "message": "success", "data": editor_doc_data}, ensure_ascii=False)
                final_user_input = f"USER_INPUT:\n```{user_input}```\n\n=====doc content====\n{doc_json}\n==================="

            session.add_message("user", final_user_input)
            try:
                # Track if this is a new conversation
                is_continuing = session.conversation_id is not None

                # Show conversation status (for debugging)
                if debug and is_continuing:
                    debug_logger.log_info(f"Continuing conversation: {session.conversation_id}")

                display.start_streaming()
                async for chunk in client.chat_completion_stream(
                    messages=session.get_messages(),
                    conversation_id=session.conversation_id,
                    mode="editor" if editor_mode else None,
                ):
                    content_delta = display.process_chunk(chunk)
                    if content_delta:
                        display.update_streaming_content(content_delta)
                    if chunk.choices and chunk.choices[0].delta:
                        delta = chunk.choices[0].delta
                        # Extract conversation_id from jarvis_metadata
                        if delta.jarvis_metadata and delta.jarvis_metadata.conversation_id:
                            if not session.conversation_id:
                                session.set_conversation_id(delta.jarvis_metadata.conversation_id)
                        # Also extract from jarvis_step.data (conversation_start event)
                        elif delta.jarvis_step and delta.jarvis_step.data.conversation_id:
                            if not session.conversation_id:
                                session.set_conversation_id(delta.jarvis_step.data.conversation_id)
                display.end_streaming()
                if display._current_content:
                    session.add_message("assistant", display._current_content)

                # Handle followup questions if any
                if display.has_pending_questions():
                    questions = display.get_pending_questions()
                    display.display_followup_questions(questions)

                    # Collect answers for each question
                    answers = []
                    for idx, question in enumerate(questions, 1):
                        if len(questions) == 1:
                            prompt_text = "Your answer: "
                        else:
                            prompt_text = f"Answer {idx}/{len(questions)}: "

                        try:
                            answer = await asyncio.get_event_loop().run_in_executor(
                                None,
                                lambda text=prompt_text: prompt_session.prompt(text)
                            )
                            if not answer and question.default_value:
                                answer = question.default_value
                                display.print_info(f"Using default: {answer}")
                            answers.append(answer)
                        except (EOFError, KeyboardInterrupt):
                            display.print_info("\nFollowup cancelled")
                            break

                    # If we got all answers, continue the conversation
                    if len(answers) == len(questions):
                        combined_answer = "\n".join(answers) if len(answers) > 1 else answers[0]
                        session.add_message("user", combined_answer)

                        # Send followup response
                        display.start_streaming()
                        async for chunk in client.chat_completion_stream(
                            messages=session.get_messages(),
                            conversation_id=session.conversation_id,
                            mode="editor" if editor_mode else None,
                        ):
                            content_delta = display.process_chunk(chunk)
                            if content_delta:
                                display.update_streaming_content(content_delta)
                        display.end_streaming()
                        if display._current_content:
                            session.add_message("assistant", display._current_content)
                
                # Save session and show conversation ID info after first message
                session_manager.auto_save_current()
                if not is_continuing and session.conversation_id:
                    # This was a new conversation - show the ID for reference
                    if debug:
                        display.print_info(f"Conversation started: {session.conversation_id}")
            except KeyboardInterrupt:
                display.print_info("\nRequest cancelled")
                continue
            except Exception as e:
                display.print_error(f"Request failed: {e}")
                continue
    finally:
        await client.close()
        debug_logger.close()
        display.print_info("Goodbye!")


async def _run_one_shot(
    query: str,
    conversation_id: Optional[str] = None,
    provider: APIProvider = APIProvider.JARVIS,
    api_key: Optional[str] = None,
    jarvis_env: Optional[str] = None,
    jarvis_url: Optional[str] = None,
    live_mode: bool = False,
    theme: str = "claude_dark",
    debug: bool = False
) -> None:
    debug_logger = init_debug_logger(enabled=debug)
    if debug:
        typer.echo(f"[DEBUG] Logging enabled. Logs will be saved to: {debug_logger.log_file}")
    
    config_manager = get_config_manager()
    config = config_manager.get()

    # Handle API key for external providers
    if provider in [APIProvider.OPENAI, APIProvider.CLAUDE]:
        if api_key:
            # Save the API key for future use
            if provider == APIProvider.OPENAI:
                config.openai.api_key = api_key
            else:
                config.claude.api_key = api_key
            config.api_provider = provider
            config_manager.save(config)
            typer.echo(f"API key saved for {provider.value}")
        else:
            # Try to use saved key
            if provider == APIProvider.OPENAI:
                api_key = config.openai.api_key
            else:
                api_key = config.claude.api_key

            if not api_key:
                typer.echo(f"Error: API key required for {provider.value}. Use -k option to provide it.")
                raise typer.Exit(1)

    # Check Jarvis config if using Jarvis
    elif provider == APIProvider.JARVIS:
        if jarvis_env:
            # Using predefined environment, override URL
            config.jarvis.api_base_url = jarvis_url
            if jarvis_env == "local":
                typer.echo(f"Using local Jarvis environment: {jarvis_url}")
            else:
                typer.echo(f"Using {jarvis_env} Jarvis environment: {jarvis_url}")

            # Check if login_code is set, if not prompt for it
            if not config.jarvis.login_code and not config.jarvis.user_id:
                from rich.prompt import Prompt
                login_code = Prompt.ask("Login Code").strip()
                config.jarvis.login_code = login_code
                config_manager.save(config)
        else:
            # Using configured Jarvis
            if not config_manager.exists() or not config.jarvis.api_base_url:
                typer.echo("No Jarvis configuration found. Run 'jvs-cli config init' first.")
                raise typer.Exit(1)

    final_live_mode = live_mode or config.display.live_mode
    final_theme = theme if theme != "claude_dark" else config.display.theme
    if final_live_mode:
        display = LiveWorkflowDisplay(config=config.display, theme_name=final_theme)
    else:
        display = DisplayManager(config=config.display)

    session_manager = SessionManager()
    if conversation_id:
        try:
            session = session_manager.load_session(conversation_id)
        except FileNotFoundError:
            display.print_error(f"Conversation not found: {conversation_id}")
            raise typer.Exit(1)
    else:
        session = session_manager.new_session()

    # Define token refresh callback
    def on_token_refresh(new_token: str, new_expires_at: str):
        """Callback to save refreshed token to config"""
        config.jarvis.jwt_token = new_token
        config.jarvis.token_expires_at = new_expires_at
        config_manager.save(config)

    # Create the appropriate client
    if provider == APIProvider.JARVIS:
        client = create_client(
            provider=provider,
            config={
                "base_url": config.jarvis.api_base_url,
                "user_id": config.jarvis.effective_user_id,
                "jwt_token": config.jarvis.jwt_token,
                "token_expires_at": config.jarvis.token_expires_at,
                "on_token_refresh": on_token_refresh,
            }
        )
    elif provider == APIProvider.OPENAI:
        client = create_client(
            provider=provider,
            config={
                "api_key": api_key,
                "model": config.openai.model,
            }
        )
    else:  # Claude
        client = create_client(
            provider=provider,
            config={
                "api_key": api_key,
                "model": config.claude.model,
            }
        )
    session.add_message("user", query)
    display.print_user_message(query)
    try:
        display.start_streaming()
        async for chunk in client.chat_completion_stream(
            messages=session.get_messages(),
            conversation_id=session.conversation_id,
        ):
            content_delta = display.process_chunk(chunk)
            if content_delta:
                display.update_streaming_content(content_delta)
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                # Extract conversation_id from jarvis_metadata
                if delta.jarvis_metadata and delta.jarvis_metadata.conversation_id:
                    if not session.conversation_id:
                        session.set_conversation_id(delta.jarvis_metadata.conversation_id)
                # Also extract from jarvis_step.data (conversation_start event)
                elif delta.jarvis_step and delta.jarvis_step.data.conversation_id:
                    if not session.conversation_id:
                        session.set_conversation_id(delta.jarvis_step.data.conversation_id)
        display.end_streaming()
        if display._current_content:
            session.add_message("assistant", display._current_content)

        # Handle followup questions if any (one-shot mode limitation: can't continue)
        if display.has_pending_questions():
            questions = display.get_pending_questions()
            display.display_followup_questions(questions)
            display.print_info("Note: Use interactive mode to answer followup questions.")

        session_manager.auto_save_current()
        if session.conversation_id:
            display.print_info(f"Conversation ID: {session.conversation_id}")
    except Exception as e:
        display.print_error(f"Request failed: {e}")
        raise typer.Exit(1)
    finally:
        await client.close()
        debug_logger.close()


if __name__ == "__main__":
    app()
