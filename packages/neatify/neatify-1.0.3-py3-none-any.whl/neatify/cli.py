import argparse
import os
from pathlib import Path

from neatify.constants import DEFAULT_FILE_PATH
from neatify.extension_manager import ExtensionManager
from neatify.utils import (get_extension, get_file_type, list_files,
                           load_default_extensions, safe_move, valid_folder)


def organise_folder(
    folder_path: str,
    manager: ExtensionManager,
):
    print(f"Using folder: {folder_path}")
    files = list_files(folder_path)

    unknowns = []
    track = {}

    for file in files:
        file_name = os.path.basename(file)
        ext = get_extension(file_name)
        file_type = get_file_type(ext, manager)

        if not file_type:
            unknowns.append(file)
            continue

        if file_type not in track:
            track[file_type] = 1
        else:
            track[file_type] += 1

        organised_folder_path = os.path.join(
            folder_path,
            f"{file_type}s",
        )
        os.makedirs(
            organised_folder_path,
            exist_ok=True,
        )

        new_file_name = os.path.join(
            organised_folder_path,
            file_name,
        )

        safe_move(
            file,
            new_file_name,
        )

    total_files_moved = 0
    for x in track.values():
        total_files_moved += x

    print(f"A total of {total_files_moved} file(s) were moved.")
    if total_files_moved > 0:
        print("Summary: ")
        for file_type in track:
            print(f"There were {track[file_type]} {file_type}(s)")
    if len(unknowns) > 0:
        print(f"There were {len(unknowns)} unknowns.")


def main():
    parser = argparse.ArgumentParser(description="Process a folder path.")

    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_FILE_PATH,
        help="Path to the extensions JSON file (default: extensions.json)",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    organise_parser = subparsers.add_parser(
        "organise",
        help="Organise a given folder",
    )

    subparsers.add_parser(
        "default",
        help="Restore the default.",
    )

    organise_parser.add_argument(
        "folder",
        type=valid_folder,
        help="Path to the target folder.",
    )

    list_parser = subparsers.add_parser("list", help="List extensions")

    add_parser = subparsers.add_parser("add", help="Add an extension to a category")
    add_parser.add_argument("category", help="Category name")
    add_parser.add_argument("extension", help="Extension to add (e.g. .jpg)")

    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove an extension from a category",
    )
    remove_parser.add_argument("category", help="Category name")
    remove_parser.add_argument("extension", help="Extension to remove")

    rmcat_parser = subparsers.add_parser("rmcat", help="Remove an entire category")
    rmcat_parser.add_argument("category", help="Category name to remove")

    clear_parser = subparsers.add_parser(
        "clear", help="Remove all categories and extensions"
    )

    args = parser.parse_args()
    manager = ExtensionManager(args.file)

    if args.command == "list":
        if not manager.data:
            print("No categories found.")

        for cat, exts in manager.data.items():
            print(f"[{cat}]")
            for e in sorted(exts):
                print(f"  .{e}")

    elif args.command == "add":
        manager.add_extension(args.category, args.extension)
        print(f"Added .{args.extension.lstrip('.')} to '{args.category}'")

    elif args.command == "remove":
        try:
            manager.remove_extension(args.category, args.extension)
            print(f"Removed .{args.extension.lstrip('.')} from '{args.category}'")
        except KeyError as e:
            print(e)

    elif args.command == "rmcat":
        if args.category in manager.data:
            del manager.data[args.category]
            manager._save()
            print(f"Removed category '{args.category}'")
        else:
            print(f"Category '{args.category}' not found.")

    elif args.command == "clear":
        confirm = (
            input("Are you sure you want to clear all extensions? (y/N): ")
            .strip()
            .lower()
        )
        if confirm == "y":
            manager._data.clear()
            manager._save()
            print("All data cleared.")
        else:
            print("Cancelled.")

    elif args.command == "organise":
        organise_folder(
            folder_path=args.folder,
            manager=manager,
        )

    elif args.command == "default":
        load_default_extensions(manager)


if __name__ == "__main__":
    main()
