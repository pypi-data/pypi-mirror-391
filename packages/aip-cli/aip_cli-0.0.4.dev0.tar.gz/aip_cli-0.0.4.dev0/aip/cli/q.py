
import os
import queue
import random
import shutil
import sys
import threading
import time

import click
import pyfiglet
import requests
from botocore.exceptions import ClientError
from click_shell import shell
from colorama import Fore, Style, init
from rich.console import Console
from rich.live import Live

# Additional imports for code formatting
from rich.markdown import Markdown
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich_gradient import Gradient
from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel
from strands_tools import retrieve

# Create a queue for status messages
status_queue = queue.Queue()

# Initialize colorama for cross-platform color support
init()

# Get terminal width for better formatting
terminal_width = shutil.get_terminal_size().columns


def get_bootstrap_config():
    """Fetch bootstrap config from the Renesas Q backend."""

    default_config = {
        "bedrock_knowledgebase_id": "JXKLX0GGDE",
        "aws_access_key_id": "",
        "gitlab_mcp_url": "",
        "aws_secret_access_key": "",
        "aws_session_token": "",
        "guardrail_id": "renesas_q_guardrail_v1",
        "guardrail_version": "1",
    }

    api_url = "https://www.ai-portal.dev1.altium.com/q/bootstrap"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        config = response.json()
        return config
    except requests.RequestException as e:
        print(f"{Fore.RED}Error fetching bootstrap config: {e}{Style.RESET_ALL}")
        sys.exit(1)


def create_callback_function(status_queue):
    """Create a highly flexible callback function that accepts any arguments."""

    def callback_function(*args, **kwargs):
        """Universal callback function that handles all event types with any arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        # Try to extract event type from args or kwargs
        event_type = None

        # Try to get event type from first argument
        if args and isinstance(args[0], str):
            event_type = args[0]

        # If not found in args, check if it's in kwargs
        if not event_type and 'event_type' in kwargs:
            event_type = kwargs['event_type']

        # Track event loop lifecycle
        if kwargs.get("init_event_loop", False):
            status_queue.put("🚀 Renesas Q  initialized")
        elif kwargs.get("start_event_loop", False):
            status_queue.put("🤔 Renesas Q assistant is thinking...")
        elif "message" in kwargs:
            status_queue.put(f"✍️  Generating detailed answer...")
        elif kwargs.get("complete", False):
            status_queue.put("🏁 Finalizing response...")
        elif kwargs.get("force_stop", False):
            status_queue.put(f"🛑 Event loop force-stopped: {kwargs.get('force_stop_reason', 'unknown reason')}")

        # Track tool usage
        if "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
            tool_name = kwargs["current_tool_use"]["name"]
            if tool_name == "retrieve":
                status_queue.put(f"🔍 Retrieving information from knowledge base")

    return callback_function


def animate_status_from_queue(status_queue, stop_event):
    """Animate status messages from a queue with progress bar."""
    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TimeElapsedColumn()
    )

    task = progress.add_task("Starting...", total=None)  # Indeterminate progress

    with Live(progress, refresh_per_second=10):  # Increase refresh rate
        while not stop_event.is_set():  # Check stop_event first thing in the loop
            try:
                # Get status message with a SHORT timeout (to check stop_event more frequently)
                status = status_queue.get(timeout=0.1)  # Reduced from 0.5 to 0.1
                progress.update(task, description=f"{status}")
            except queue.Empty:
                # Check stop_event again in case it was set while waiting
                if stop_event.is_set():
                    break
                continue

            # Check stop_event after processing message too
            if stop_event.is_set():
                break

        # Optional: Show completion status briefly
        progress.update(task, description="Done!")
        time.sleep(0.2)  # Brief pause to show final status



# Fancy banner function
def print_banner():
    console = Console()
    font_list = ["smmono12", "kban", "mono9", "3-d", "blocky"]
    print("\n")
    # Pick a random font
    selected_font = random.choice(font_list)
    figlet_text = pyfiglet.figlet_format("Renesas Q", font=selected_font)

    with Live(console=console, refresh_per_second=2) as live:
        for i in range(5):  # Number of animation frames
            rainbow_text = Gradient(figlet_text, rainbow=True,
            justify="center")
            live.update(rainbow_text)
            time.sleep(0.2)

    console.print(
    Gradient(
       "Your AI assistant for the Renesas Vision Designer CLI",
        rainbow=True,
        justify="center"
    )
    )
    print("\n")
    print()


def typing_effect(text, speed=0.01):
    """Create a typing effect for text output"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(speed)
    print()



@shell(
    # prompt='q > ',
    prompt=f"{Style.BRIGHT}{Fore.CYAN}Q >{Style.RESET_ALL} ",
    intro=""
)
@click.pass_context
def q(ctx):
    """Interactive Q shell for Renesas Vision Designer CLI."""
    # Print our custom banner
    print_banner()

    typing_effect(f"{Style.BRIGHT}Welcome to Renesas Q!{Style.RESET_ALL} How can I help you today?")
    print(f"\n{Fore.YELLOW}Available commands:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}chat{Style.RESET_ALL} - Start an interactive chat session")
    print(f"  {Fore.GREEN}help{Style.RESET_ALL} - How Renesas Q agent can assist you?")
    print(f"\n{Fore.YELLOW}Or just type your question directly!{Style.RESET_ALL}\n")


@q.command()
def help():
    """Show how this Renesas Q agent can assist you."""
    help_text = f"""\n{Fore.YELLOW}
    Renesas Q is your intelligent assistant for Renesas Vision Designer CLI. {Style.RESET_ALL}
    
    Here are some ways I can assist you:

    - Answer questions about Renesas Vision Designer features and capabilities
    - Provide guidance on using Vision Designer, Reaction, and other tools
    - Help troubleshoot common issues
    - Offer best practices for AI model development and deployment
    - Assist with configuration and setup tasks
    - And much more!

    \n{Fore.YELLOW} Common Topics{Style.RESET_ALL}
    • Getting started guides
    • Installation and setup
    • Model Training & deployment workflows
    • Configuration parameters
    • Troubleshooting issues
    • Best practices
    • API documentation

    \n{Fore.YELLOW} How to ask for help{Style.RESET_ALL}:
    • Be specific about what you're trying to do
    • Mention which component you're working with
    • Include any error messages you're encountering
    • Ask about specific features or workflows

    \n{Fore.YELLOW} Examples of questions I can answer{Style.RESET_ALL}:

    • "How do I deploy a model using Vision Designer?"
    • "What are the configuration options for Reaction?"
    • "What pre-trained models are available?"
    • "I'm getting an error when trying to..."

    \n{Fore.GREEN}Just type "{Fore.YELLOW}chat{Style.RESET_ALL}{Fore.GREEN}" and ask your question, and I'll help you out!{Style.RESET_ALL}
    \n{Fore.GREEN}If you want to see debug information, use "{Fore.YELLOW}chat --debug{Style.RESET_ALL}{Fore.GREEN}" command.{Style.RESET_ALL}\n
    """
    console = Console()
    md = Markdown(help_text)
    console.print(md)


@q.command()
@click.option('--debug', is_flag=True, help='Show agent debug information.')
def chat(debug):
    """Start an interactive chat session with the Renesas Q agent."""
    print(f"\n{Style.BRIGHT}Starting chat session with Renesas Q{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' to end the session{Style.RESET_ALL}\n")
    # Get client from shell context
    if debug:
        print(f"{Fore.CYAN}Debug mode enabled. Agent Debug information will be displayed.{Style.RESET_ALL}\n")
    while True:
        # Get user input with a styled prompt
        user_input = click.prompt(f"{Style.BRIGHT}{Fore.GREEN}You{Style.RESET_ALL}",
                                 prompt_suffix=f"{Style.BRIGHT}{Fore.WHITE} >{Style.RESET_ALL} ")

        if user_input.lower() in ('exit', 'quit', 'bye'):
            print(f"\n{Fore.CYAN}Thank you for using Renesas Q. Goodbye!{Style.RESET_ALL}")
            break
        # Create a queue for status messages
        status_queue = queue.Queue()
        # Initialize these variables outside the try block
        stop_event = threading.Event()
        # Start animation thread that reads from queue
        animation_thread = threading.Thread(
                target=animate_status_from_queue,
                args=(status_queue, stop_event)
        )
        try:
            config = get_bootstrap_config()
            kb_id = config.get("bedrock_knowledgebase_id")
            os.environ["AWS_ACCESS_KEY_ID"] = config.get("aws_access_key_id")
            os.environ["AWS_SECRET_ACCESS_KEY"] = config.get("aws_secret_access_key")
            os.environ["AWS_SESSION_TOKEN"] = config.get("aws_session_token")
            guardrail_id = config.get("guardrail_id", "renesas_q_guardrail_v1")
            guardrail_version = config.get("guardrail_version", "1")
            region = "ap-northeast-1"
            model_id = "jp.anthropic.claude-haiku-4-5-20251001-v1:0"
            os.environ["AWS_REGION"] = region

            bedrock_model = BedrockModel(
            model_id=model_id,
            region_name=region,
            max_tokens=2048,
            streaming=True,
            temperature=0.2,
            guardrail_id=guardrail_id,           # Your Bedrock guardrail ID
            guardrail_version=guardrail_version,  # Guardrail version
            )
            # Configure conversation management
            conversation_manager = SlidingWindowConversationManager(
                window_size=2,  # Limit history size
            )

            # Start animation thread that reads from queue
            animation_thread = threading.Thread(
                target=animate_status_from_queue,
                args=(status_queue, stop_event)
            )
            animation_thread.daemon = True  # Make sure thread doesn't block exit
            animation_thread.start()

            # Add initial message
            status_queue.put("Starting agent...")

            # Create a single callback function
            callback_function = create_callback_function(status_queue)

            # Create a configured Bedrock model
            agent = Agent(
                    system_prompt=f"""You are an intelligent assistant for Renesas Vision Designer CLI. 
                    Format your responses using Markdown.
                    Provide concise facts about Vision Designer, Reaction, etc. Use knowledge base with ID {kb_id}""",
                    tools=[retrieve],
                    model=bedrock_model,
                    callback_handler=callback_function,
                    conversation_manager=conversation_manager,

                )

            # print starting time
            start_time = time.time()
            response = agent(user_input)
            # Access metrics through the AgentResult
            if debug:
                print(f"{Fore.GREEN}--- Agent Debug Information ---{Style.RESET_ALL}")
                print(f"\n{Fore.GREEN}Model used: {model_id}")
                print(f"{Fore.GREEN}Total tokens: {response.metrics.accumulated_usage['totalTokens']}")
                print(f"{Fore.GREEN}Input tokens: {response.metrics.accumulated_usage['inputTokens']}")
                print(f"{Fore.GREEN}Output tokens: {response.metrics.accumulated_usage['outputTokens']}")
                print(f"{Fore.GREEN}Total latency of model requests in seconds: {response.metrics.accumulated_metrics['latencyMs'] / 1000:.2f}")
                if 'retrieve' in response.metrics.tool_metrics:
                    print(f"{Fore.GREEN}Knowledge base usage count: {response.metrics.tool_metrics['retrieve'].call_count}")
                    print(f"{Fore.GREEN}Knowledge base usage total time {response.metrics.tool_metrics['retrieve'].total_time:.2f} seconds")
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"{Fore.MAGENTA}Response generated in {elapsed_time:.2f} seconds.{Style.RESET_ALL}\n")
                print(f"{Fore.GREEN}--- End of Debug Information ---{Style.RESET_ALL}\n")

            # Signal animation to stop
            stop_event.set()

            # Wait for animation to finish
            animation_thread.join()

            # If thread is still alive after timeout, print a warning
            if animation_thread.is_alive():
                print(f"\n{Fore.YELLOW}Warning: Animation thread is still running.{Style.RESET_ALL}")


            # Clear the "Processing" message
            sys.stdout.write("\r" + " " * terminal_width + "\r")

            # Normalize AgentResult to a string
            if isinstance(response, str):
                resp_text = response
            else:
                resp_text = None
                for attr in ('text', 'output', 'content', 'result'):
                    if hasattr(response, attr):
                        resp_text = getattr(response, attr)
                        break
                if resp_text is None:
                    resp_text = str(response)

            print(f"\n{Style.BRIGHT}{Fore.CYAN}Renesas Q:{Style.RESET_ALL} ")
            console = Console()
            md = Markdown(resp_text)

            console.print(md)
            sys.stdout.write("\r" + " " * terminal_width + "\r")
        except ClientError as e:
            sys.stdout.write("\r" + " " * terminal_width + "\r")
            if debug:
                print(f"\n{Fore.RED}Client Error Details:{Style.RESET_ALL} {e!s}")
            print(f"{Fore.YELLOW}Please re-authenticate using the 'aip login' command.{Style.RESET_ALL}\n")
        except Exception as e:
            sys.stdout.write("\r" + " " * terminal_width + "\r")
            if debug:
                print(f"\n{Fore.RED}Exception Details:{Style.RESET_ALL} {e!s}")
            print(f"{Fore.YELLOW}Unknown error occurred.{Style.RESET_ALL}\n")
        finally:
            stop_event.set()
            # Wait for animation to finish
            if animation_thread is not None and animation_thread.is_alive():
                animation_thread.join()


if __name__ == '__main__':
    q()
