import argparse
import json
import os
import re
from os.path import exists
from pathlib import Path
from typing import List, Optional

from neatify.extension_manager import ExtensionManager


def valid_folder(path: str):
    """Validate that the given path is an existing directory."""
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid directory path.")
    return os.path.abspath(path)


def list_files(folder_path: str):
    files = os.listdir(folder_path)
    temp: List[str] = []
    for f in files:
        file_path = os.path.join(folder_path, f)
        if os.path.isfile(file_path):
            temp.append(file_path)
    return temp


def get_extension(file_name: str):
    ext = file_name.split(".")[-1]
    return ext.lower()


def get_file_type(ext: str, manager: ExtensionManager) -> Optional[str]:
    for file_type in manager.data:
        if ext in manager.data[file_type]:
            return file_type
    return None


def load_default_extensions(
    extension_manager: ExtensionManager,
):
    path = Path(__file__)
    file_path = path.parent.parent / "default_extensions.json"
    temp_file_path = path.parent / "default_extensions.json"
    x = file_path if file_path.exists() else temp_file_path
    with open(x) as f:
        data = f.read()
        default_extensions = json.loads(data)
    for cat in default_extensions:
        for ext in default_extensions[cat]:
            extension_manager.add_extension(cat, ext)


def increment_filename(name_with_ext: str):
    name, *ext_parts = name_with_ext.split(".")
    ext = ".".join(ext_parts) if ext_parts else ""

    pattern = r"^(.*)\((\d+)\)$"
    m = re.match(pattern, name.strip())

    if m:
        base_name, number = m.groups()
        new_number = int(number) + 1
        new_name = f"{base_name.strip()} ({new_number})"
    else:
        new_name = f"{name.strip()} (1)"

    # Recombine with extension (if any)
    if ext:
        return f"{new_name}.{ext}"
    return new_name


def safe_move(
    old_file_path: str,
    new_file_path: str,
):
    if os.path.exists(new_file_path):
        print(f"There is already a file at: {new_file_path}")

        file_name = os.path.basename(new_file_path)
        new_file_name = increment_filename(file_name)
        new_file_path = os.path.join(
            os.path.dirname(new_file_path),
            new_file_name,
        )
        print(f"Renaming it to: {new_file_name}")

        safe_move(old_file_path, new_file_path)
        return

    os.rename(old_file_path, new_file_path)
    return
