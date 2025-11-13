"""
This script is run by the target create_cairo_lang_package_zip to create the cairo-lang package
zip file.
"""

import os
import shutil
import subprocess
import sys

from starkware.python.utils import get_build_dir_path, get_source_dir_path

INIT_FILE_CONTENT = "__path__ = __import__('pkgutil').extend_path(__path__, __name__)\n"


def add_init_files(path: str):
    """
    Adds __init__.py files (with INIT_FILE_CONTENT) to every directory which does not have an init
    file and contains a ".py" file or a sub directory.
    """

    for path, directories, files in os.walk(path):
        if "__init__.py" in files:
            continue

        if len(directories) > 0 or any(file_name.endswith(".py") for file_name in files):
            with open(os.path.join(path, "__init__.py"), "w", encoding="utf-8") as init_file:
                init_file.write(INIT_FILE_CONTENT)


if __name__ == "__main__":
    dst_dir = get_build_dir_path("src")

    # Add init files.
    add_init_files(os.path.join(dst_dir, "starkware"))
    add_init_files(os.path.join(dst_dir, "services"))

    source_root = get_source_dir_path(default_value=os.getcwd())

    def copy_from_source(relative_path: str, destination: str):
        shutil.copy(os.path.join(source_root, relative_path), destination)

    def copy_directory(relative_path: str):
        source_path = os.path.join(source_root, relative_path)
        if relative_path.startswith("src/"):
            target_subpath = os.path.relpath(relative_path, "src")
        else:
            target_subpath = relative_path
        destination_path = os.path.join(dst_dir, target_subpath)
        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)

    copy_from_source("src/starkware/cairo/lang/setup.py", dst_dir)
    copy_from_source("src/starkware/cairo/lang/MANIFEST.in", dst_dir)
    copy_from_source("scripts/requirements-gen.txt", os.path.join(dst_dir, "requirements.txt"))
    copy_from_source("README.md", dst_dir)
    copy_directory("src/starkware/starknet/common")

    # Run setup.py.
    subprocess.check_call([sys.executable, "setup.py", "sdist", "--format=gztar"], cwd=dst_dir)

    with open(
        os.path.join(source_root, "src/starkware/cairo/lang/VERSION"), "r", encoding="utf-8"
    ) as f:
        version = f.read().strip("\n")
    shutil.copy(f"{dst_dir}/dist/cairo-lang-{version}.tar.gz", ".")
