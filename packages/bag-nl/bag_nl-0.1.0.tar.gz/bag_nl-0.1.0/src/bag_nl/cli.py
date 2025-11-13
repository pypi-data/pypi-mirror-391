import argparse
import sys

from .importer import importer


def cmd_import(args: argparse.Namespace) -> int:
    """
    Handle the 'import' subcommand.

    Expected behavior:
    - Calls importer(db, collections=None|list, test=False|int)
    """
    db = args.db

    # Collections: comma-separated list or None for default
    collections = args.collections
    if collections:
        # Allow both comma-separated and space-separated usage
        # e.g. "--collections vbo,num" or "--collections vbo num"
        if isinstance(collections, list):
            # argparse with nargs="*" -> list; support both forms:
            #   bag-nl import DB --collections vbo num
            #   bag-nl import DB --collections vbo,num
            normalized = []
            for item in collections:
                normalized.extend(part for part in item.split(",") if part)
            collections = normalized
        else:
            collections = [c for c in str(collections).split(",") if c]

    # Test flag: if provided without value -> True;
    # if given a positive integer, limit rows to that many.
    test = False
    if args.test is not None:
        if args.test is True:
            test = True
        else:
            # args.test is an int via argparse type
            if args.test <= 0:
                print("--test value must be positive", file=sys.stderr)
                return 1
            test = args.test

    try:
        importer(db=db, collections=collections, test=test)
    except Exception as exc:  # noqa: BLE001
        if args.verbose:
            print(f"Import failed: {exc!r}", file=sys.stderr)
        else:
            print(f"Import failed: {exc}", file=sys.stderr)
        return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bag-nl",
        description="BAG-NL tools: import BAG data into a database."
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose error output."
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="command",
        required=True
    )

    # 'import' subcommand
    import_parser = subparsers.add_parser(
        "import",
        help="Import BAG data into the specified database."
    )

    import_parser.add_argument(
        "db",
        help=(
            "Database path or DSN understood by the configured 'connect' "
            "function (e.g. a SQLite file path)."
        ),
    )

    import_parser.add_argument(
        "-c",
        "--collections",
        nargs="*",
        help=(
            "Optional list of collections to import. "
            "If omitted, the default set is used. "
            "Examples: "
            "'--collections vbo num opr' or '--collections vbo,num,opr'."
        ),
    )

    import_parser.add_argument(
        "--test",
        nargs="?",
        const=True,
        type=int,
        help=(
            "Test mode: if provided without a value, import only a small sample; "
            "if provided with an integer N, import at most N rows per collection."
        ),
    )

    import_parser.set_defaults(func=cmd_import)

    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Entry point for the 'bag-nl' console script.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Ensure verbose flag is available to subcommands
    if not hasattr(args, "verbose"):
        args.verbose = False

    if hasattr(args, "func"):
        return args.func(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

