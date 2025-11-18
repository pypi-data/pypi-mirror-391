"""Command-line interface for claude-hooks."""

import argparse
import sys

from claude_hooks.main import HOOK_CONFIG, add_hook, install_all_hooks


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: List of arguments to parse. If None, uses sys.argv.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Configure Claude Code hooks in your project.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add subcommand
    add_parser = subparsers.add_parser(
        "add",
        help="Add a hook to your project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Available hooks:\n"
        + "\n".join(
            f"  {name:20} {config['description']}"
            for name, config in HOOK_CONFIG.items()
        ),
    )
    add_parser.add_argument(
        "hook_name",
        type=str,
        choices=list(HOOK_CONFIG.keys()),
        metavar="HOOK",
        help="Name of hook to add (see available hooks below)",
    )

    # Install subcommand
    subparsers.add_parser(
        "install",
        help="Create hook scripts and configure all hooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Creates .sh scripts and updates settings.local.json for:\n"
        + "\n".join(
            f"  {name:20} {config['description']}"
            for name, config in HOOK_CONFIG.items()
        ),
    )

    return parser.parse_args(args)


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        args = parse_args()

        if args.command is None:
            print(
                "Error: No command specified. Use 'add' to add a hook.", file=sys.stderr
            )
            return 1

        if args.command == "add":
            add_hook(args.hook_name)
            return 0

        if args.command == "install":
            install_all_hooks()
            return 0

        return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
