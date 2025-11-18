"""CLI interface for CommitAid."""

import sys
from .config import Config
from .workflow import run_workflow, WorkflowError


def print_help():
    """Print help message."""
    help_text = """
CommitAid - AI-powered Git commit message generator

USAGE:
    commitaid [COMMAND] [OPTIONS]

COMMANDS:
    (no command)              Generate a commit message using Claude AI
    config set <key> <value>  Set a configuration value
    config view [key]         View configuration (all or specific key)
    help                      Show this help message

CONFIGURATION KEYS:
    commit-spec     Custom commit specification/guidelines for Claude
    auto-signoff    Enable/disable automatic Signed-off-by line (enabled|disabled)

EXAMPLES:
    # Generate a commit message
    commitaid

    # Set custom commit specification (overrides default Conventional Commits)
    commitaid config set commit-spec "Use Angular style with JIRA ticket numbers"

    # Enable auto sign-off
    commitaid config set auto-signoff enabled

    # View all configuration
    commitaid config view

    # View specific configuration
    commitaid config view commit-spec

WORKFLOW:
    1. Checks if you're in a git repository
    2. Checks if Claude CLI is installed
    3. Installs /commitaid command if needed
    4. Runs Claude to generate commit message
    5. Opens editor for you to review/edit
    6. Creates git commit with the message

REQUIREMENTS:
    - git installed and in PATH
    - Claude CLI installed (https://docs.claude.com/en/docs/claude-code)
    - Active git repository
"""
    print(help_text)


def handle_config(args: list):
    """Handle config subcommand."""
    if len(args) < 1:
        print("Error: config requires a subcommand (set or view)")
        print("Usage: commitaid config set <key> <value>")
        print("       commitaid config view [key]")
        sys.exit(1)

    subcommand = args[0]
    config = Config()

    if subcommand == "set":
        if len(args) < 3:
            print("Error: config set requires <key> and <value>")
            print("Usage: commitaid config set <key> <value>")
            sys.exit(1)

        key = args[1]
        value = args[2]
        if not config.set(key, value):
            sys.exit(1)

    elif subcommand == "view":
        key = args[1] if len(args) > 1 else None
        config.view(key)

    else:
        print(f"Error: Unknown config subcommand '{subcommand}'")
        print("Valid subcommands: set, view")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]

    # Handle help command
    if len(args) > 0 and args[0] == "help":
        print_help()
        return

    # Handle config command
    if len(args) > 0 and args[0] == "config":
        handle_config(args[1:])
        return

    # Handle unknown commands
    if len(args) > 0 and not args[0].startswith("-"):
        print(f"Error: Unknown command '{args[0]}'")
        print("Run 'commitaid help' for usage information")
        sys.exit(1)

    # Run main workflow
    try:
        config = Config()
        commit_spec = config.get("commit-spec")
        auto_signoff_config = config.get("auto-signoff")
        auto_signoff = auto_signoff_config == "enabled" if auto_signoff_config else False

        run_workflow(commit_spec=commit_spec, auto_signoff=auto_signoff)

    except WorkflowError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
