import argparse
import shutil
from pathlib import Path
import importlib.resources as resources
from importlib.metadata import version, PackageNotFoundError


def list_docs():
    """List all documentation templates included in the package."""
    package_path = resources.files("enterprise_docs.templates")
    for f in package_path.iterdir():
        if f.suffix == ".md":
            print(f.name)


def copy_docs(destination: str):
    """Copy documentation templates to the specified directory."""
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)

    src = resources.files("enterprise_docs.templates")
    for f in src.iterdir():
        if f.suffix == ".md":
            shutil.copy(f, dest / f.name)

    print(f"✅ Copied documentation templates to {dest.resolve()}")


def show_version():
    """Display the installed version of enterprise-docs."""
    try:
        v = version("enterprise-docs")
    except PackageNotFoundError:
        v = "unknown"
    print(f"enterprise-docs {v}")


def main():
    parser = argparse.ArgumentParser(
        description="Enterprise Docs Manager — manage and sync standard documentation templates."
    )
    parser.add_argument(
        "command",
        choices=["list", "sync", "version"],
        help="Command to run: list available docs, sync to folder, or show version.",
    )
    parser.add_argument("--to", default="./docs", help="Destination directory for sync (default: ./docs)")
    args = parser.parse_args()

    if args.command == "list":
        list_docs()
    elif args.command == "sync":
        copy_docs(args.to)
    elif args.command == "version":
        show_version()


if __name__ == "__main__":
    main()