#!/usr/bin/env python3
"""RSS Manager CLI - Main entry point.

A command-line tool for managing RSS feeds with support for:
- Feed discovery
- Feed subscription management
- OPML import/export
- RSSHub route browsing
"""
import argparse
import sys
import subprocess
from pathlib import Path

# Command mapping
COMMANDS = {
    "discover": "rss-discover.py",
    "add": "rss-add.py",
    "list": "rss-list.py",
    "import": "rss-import.py",
    "export": "rss-export.py",
    "rsshub": "rss-rsshub.py",
}


def get_skill_dir() -> Path:
    """Get the skill directory."""
    return Path(__file__).parent


def run_command(command: str, args: list):
    """Run a subcommand by delegating to the appropriate script."""
    if command not in COMMANDS:
        print(f"Unknown command: {command}")
        print(f"Run '{sys.argv[0]} --help' for usage.")
        sys.exit(1)

    script_path = get_skill_dir() / COMMANDS[command]

    if not script_path.exists():
        print(f"Error: Command script not found: {script_path}")
        sys.exit(1)

    # Run the subcommand script
    result = subprocess.run([sys.executable, str(script_path)] + args)
    sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        prog="rss",
        description="RSS Manager - Manage your RSS feeds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  discover    Discover RSS feeds from a website
  add         Add an RSS feed to your subscriptions
  list        List all subscribed feeds
  import      Import feeds from an OPML file
  export      Export feeds to an OPML file
  rsshub      Browse RSSHub routes

Use "rss <command> --help" for more information about a command.

Examples:
  rss discover https://example.com
  rss add https://example.com/feed.xml --category tech
  rss list --category news
  rss import ~/Downloads/feeds.opml
  rss export backup.opml
  rss rsshub --list
        """
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=list(COMMANDS.keys()),
        help="Command to run"
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments for the command"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Remove '--' from args if present (added by argparse)
    command_args = args.args
    if command_args and command_args[0] == "--":
        command_args = command_args[1:]

    run_command(args.command, command_args)


if __name__ == "__main__":
    main()
