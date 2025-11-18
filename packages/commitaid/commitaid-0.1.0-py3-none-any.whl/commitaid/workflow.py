"""Main workflow logic for CommitAid."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


# Placeholder URL for the commitaid slash command
COMMITAID_COMMAND_URL = "https://raw.githubusercontent.com/Ruclo/commitaid/main/commitaid-command.md"

# Default commit specification (Conventional Commits)
DEFAULT_COMMIT_SPEC = """The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

- Commits MUST be prefixed with a type, which consists of a noun, feat, fix, etc., followed by the OPTIONAL scope, OPTIONAL !, and REQUIRED terminal colon and space.
- The type feat MUST be used when a commit adds a new feature to your application or library.
- The type fix MUST be used when a commit represents a bug fix for your application.
- A scope MAY be provided after a type. A scope MUST consist of a noun describing a section of the codebase surrounded by parenthesis, e.g., fix(parser):
- A description MUST immediately follow the colon and space after the type/scope prefix. The description is a short summary of the code changes, e.g., fix: array parsing issue when multiple spaces were contained in string.
- A longer commit body MAY be provided after the short description, providing additional contextual information about the code changes. The body MUST begin one blank line after the description.
- A commit body is free-form and MAY consist of any number of newline separated paragraphs.
- One or more footers MAY be provided one blank line after the body. Each footer MUST consist of a word token, followed by either a :<space> or <space># separator, followed by a string value (this is inspired by the git trailer convention).
- A footer's token MUST use - in place of whitespace characters, e.g., Acked-by (this helps differentiate the footer section from a multi-paragraph body). An exception is made for BREAKING CHANGE, which MAY also be used as a token.
- A footer's value MAY contain spaces and newlines, and parsing MUST terminate when the next valid footer token/separator pair is observed.
- Breaking changes MUST be indicated in the type/scope prefix of a commit, or as an entry in the footer.
- If included as a footer, a breaking change MUST consist of the uppercase text BREAKING CHANGE, followed by a colon, space, and description, e.g., BREAKING CHANGE: environment variables now take precedence over config files.
- If included in the type/scope prefix, breaking changes MUST be indicated by a ! immediately before the :. If ! is used, BREAKING CHANGE: MAY be omitted from the footer section, and the commit description SHALL be used to describe the breaking change.
- Types other than feat and fix MAY be used in your commit messages, e.g., docs: update ref docs.
- The units of information that make up Conventional Commits MUST NOT be treated as case sensitive by implementors, with the exception of BREAKING CHANGE which MUST be uppercase.
- BREAKING-CHANGE MUST be synonymous with BREAKING CHANGE, when used as a token in a footer.
- Long descriptions in the body or footers MUST be wrapped at 72 characters.
"""


class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH."""
    try:
        subprocess.run(
            ["which", command],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_git_repo() -> bool:
    """Check if current directory is a git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_staged_changes() -> bool:
    """
    Check if there are any staged changes ready to commit.

    Returns:
        True if there are staged changes, False otherwise
    """
    try:
        # git diff --cached --quiet returns 0 if no changes, 1 if there are changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True,
            text=True
        )
        return result.returncode == 1
    except subprocess.CalledProcessError:
        return False


def get_git_root() -> Optional[Path]:
    """Get the root directory of the git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return None


def check_claude_command_exists() -> bool:
    """Check if /commitaid command exists in Claude CLI."""
    claude_commands_dir = Path.home() / ".claude" / "commands"
    command_file = claude_commands_dir / "commitaid.md"
    return command_file.exists()


def install_claude_command() -> bool:
    """Install the /commitaid command for Claude CLI."""
    claude_commands_dir = Path.home() / ".claude" / "commands"
    claude_commands_dir.mkdir(parents=True, exist_ok=True)
    command_file = claude_commands_dir / "commitaid.md"

    print("Installing /commitaid command for Claude CLI...")
    try:
        # Fetch the command file from GitHub
        result = subprocess.run(
            ["curl", "-fsSL", COMMITAID_COMMAND_URL],
            check=True,
            capture_output=True,
            text=True
        )

        with open(command_file, 'w') as f:
            f.write(result.stdout)

        print("✓ /commitaid command installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to download command file: {e}")
        return False
    except IOError as e:
        print(f"Error: Failed to write command file: {e}")
        return False


def run_claude_commitaid(commit_spec: Optional[str] = None) -> Optional[str]:
    """
    Run Claude CLI with /commitaid command.

    Args:
        commit_spec: Optional commit specification to pass to Claude.
                    If None, uses DEFAULT_COMMIT_SPEC.

    Returns:
        Generated commit message or None if failed
    """
    env = os.environ.copy()
    # Always set COMMITAID_SPEC, using default if not provided
    env["COMMITAID_SPEC"] = commit_spec if commit_spec else DEFAULT_COMMIT_SPEC

    try:
        result = subprocess.run(
            ["claude", "-p", "/commitaid"],
            check=True,
            capture_output=True,
            text=True,
            env=env
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: Claude command failed: {e}")
        if e.stderr:
            print(e.stderr)
        return None


def open_in_editor(content: str) -> Optional[str]:
    """
    Open content in user's preferred editor.

    Args:
        content: Initial content to edit

    Returns:
        Edited content or None if cancelled
    """
    # Get git root for tempfile location
    git_root = get_git_root()
    if not git_root:
        raise WorkflowError("Could not determine git root directory")

    git_dir = git_root / ".git"
    if not git_dir.exists():
        raise WorkflowError(".git directory not found")

    # Create tempfile in .git directory
    temp_fd, temp_path = tempfile.mkstemp(
        suffix=".txt",
        prefix="COMMIT_EDITMSG_",
        dir=str(git_dir),
        text=True
    )

    try:
        # Write initial content
        with os.fdopen(temp_fd, 'w') as f:
            f.write(content)

        # Get editor from environment or use default
        editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "vim"))

        # Open editor
        subprocess.run([editor, temp_path], check=True)

        # Ask for confirmation before proceeding
        print("\nProceed with this commit message? (y/n): ", end='', flush=True)
        confirmation = input().strip().lower()

        if confirmation not in ('y', 'yes'):
            print("Commit cancelled")
            return None

        # Read edited content
        with open(temp_path, 'r') as f:
            edited_content = f.read().strip()

        return edited_content if edited_content else None

    except subprocess.CalledProcessError as e:
        print(f"Error: Editor failed: {e}")
        return None
    except IOError as e:
        print(f"Error: Failed to read/write tempfile: {e}")
        return None
    finally:
        # Clean up tempfile
        try:
            os.unlink(temp_path)
        except OSError:
            pass


def run_git_commit(message: str, signoff: bool = False) -> bool:
    """
    Run git commit with the provided message.

    Args:
        message: Commit message
        signoff: Whether to add Signed-off-by line

    Returns:
        True if successful, False otherwise
    """
    cmd = ["git", "commit", "-m", message]
    if signoff:
        cmd.append("-s")

    try:
        subprocess.run(cmd, check=True)
        print("✓ Commit created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Git commit failed: {e}")
        return False


def run_workflow(commit_spec: Optional[str] = None, auto_signoff: bool = False):
    """
    Run the main CommitAid workflow.

    Args:
        commit_spec: Optional commit specification
        auto_signoff: Whether to add Signed-off-by line
    """
    # Check if git is installed
    if not check_command_exists("git"):
        raise WorkflowError("git is not installed or not in PATH")

    # Check if in git repo
    if not check_git_repo():
        raise WorkflowError("Not in a git repository")

    # Check for staged changes
    if not check_staged_changes():
        raise WorkflowError(
            "No staged changes found\n"
            "Use 'git add' to stage changes before running commitaid"
        )

    # Display configuration
    print(f"Auto sign-off: {'enabled' if auto_signoff else 'disabled'}")
    if commit_spec:
        print(f"Commit spec: custom")
    else:
        print(f"Commit spec: Conventional Commits (default)")

    # Check if claude CLI is installed
    if not check_command_exists("claude"):
        raise WorkflowError(
            "Claude CLI is not installed or not in PATH\n"
            "Install it from: https://docs.claude.com/en/docs/claude-code"
        )

    # Check if /commitaid command exists, install if not
    if not check_claude_command_exists():
        if not install_claude_command():
            raise WorkflowError("Failed to install /commitaid command")

    # Run Claude to generate commit message
    print("Generating commit message with Claude...")
    commit_message = run_claude_commitaid(commit_spec)

    if not commit_message:
        raise WorkflowError("Failed to generate commit message")

    # Open in editor for user to review/edit
    print("Opening editor for review...")
    edited_message = open_in_editor(commit_message)

    if not edited_message:
        print("Commit cancelled (empty message)")
        return

    # Run git commit
    run_git_commit(edited_message, signoff=auto_signoff)
