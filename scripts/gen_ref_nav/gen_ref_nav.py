"""Script to generate the documentation pages and navigation for our library.

Important: remember to change PATH_LIBRARY to whatever name your package
folder has!!
"""

import sys
import os
from pathlib import Path

import mkdocs_gen_files


nav = mkdocs_gen_files.Nav()
PATH_LIBRARY = "cybersyn"  # change this with your library's name


if os.path.isdir(PATH_LIBRARY) is False:
    sys.exit(
        "Package folder was not found. Please change the PATH_LIBRARY"
        " variable in the docs/scripts/gen_ref_nav.py script."
    )


for path in sorted(Path(PATH_LIBRARY).rglob("*.py")):
    module_path = path.relative_to("").with_suffix("")
    doc_path = path.relative_to(PATH_LIBRARY).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}\n")
        fd.write("\thandler: python\n")
        fd.write("\toptions:\n")
        fd.write("\t\tshow_root_heading: true\n")
        fd.write("\t\tshow_source: true\n")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.txt", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
