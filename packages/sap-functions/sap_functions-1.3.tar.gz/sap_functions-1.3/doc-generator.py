import sys
import importlib
import pkgutil
import inspect
from pathlib import Path


def generate_md_doc_for_codebase(module_name: str, output_file="README.md"):
    """Generate a single Markdown documentation file for all classes and functions in a package."""

    # ensure src directory is at the front
    src_path = str(Path("src").resolve())
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    importlib.invalidate_caches()

    package = importlib.import_module(module_name)

    docs = [f"""
# sap_functions
Library with utility classes and functions to facilitate the development of SAP automations in python.

This module is built on top of SAP Scripting and aims to making the development of automated workflows easier and quicker.

## Implementation example
```python
from sap_functions import SAP

sap = SAP()
sap.select_transaction("COOIS")
```
This script:

Checks for existant SAP GUI instances.
Connects to that instance.
Write "COOIS" in the transaction field.
# Classes overview
"""]

    for _, submodule_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            submodule = importlib.import_module(submodule_name)
            submodule = importlib.reload(submodule)
        except Exception as e:
            print(f"Skipping {submodule_name}: {e}")
            continue

        docs.append(f"\n## Module `{submodule_name}`\n")

        # classes
        classes = inspect.getmembers(submodule, inspect.isclass)
        classes = [c for c in classes if getattr(c[1], "__module__", "") == submodule_name]
        class_docs = []

        for class_name, cls in classes:
            class_docs.append(f"### Class `{class_name}`\n")

            attrs = [
                a for a in vars(cls)
                if not callable(getattr(cls, a)) and not a.startswith("__")
            ]
            if attrs:
                class_docs.append("**Attributes:**")
                for attr in attrs:
                    class_docs.append(f"- `{attr}`")
                class_docs.append("")

            methods = inspect.getmembers(cls, inspect.isfunction)
            if methods:
                class_docs.append("**Methods:**")
                for _, method in methods:
                    class_docs.append(_format_function_doc(method))
                class_docs.append("")

        if class_docs:
            docs.extend(class_docs)

        # top-level functions
        functions = inspect.getmembers(submodule, inspect.isfunction)
        func_docs = [
            _format_function_doc(func)
            for _, func in functions
            if getattr(func, "__module__", "").startswith(module_name)
        ]

        if func_docs and not class_docs:
            docs.append("### Top-level Functions\n")
            docs.extend(func_docs)
            docs.append("")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(docs))

    print(f"Documentation saved to `{output_file}`")


def _format_function_doc(func):
    """Format a function/method signature into Markdown."""
    # unwrap decorators
    target = getattr(func, "__wrapped__", func)

    sig = inspect.signature(target)
    params = []

    for name, p in sig.parameters.items():
        prefix = "*" if p.kind == p.VAR_POSITIONAL else "**" if p.kind == p.VAR_KEYWORD else ""
        segment = f"{prefix}{name}"

        if p.annotation != inspect._empty:
            ann = p.annotation.__name__ if hasattr(p.annotation, "__name__") else str(p.annotation)
            segment += f": {ann}"

        if p.default != inspect._empty:
            segment += f" = {repr(p.default)}"

        params.append(segment)

    params_str = ", ".join(params)

    ret = ""
    if sig.return_annotation != inspect._empty:
        ann = sig.return_annotation
        ret = f" -> {ann.__name__ if hasattr(ann, '__name__') else ann}"

    doc = inspect.getdoc(target) or inspect.getdoc(func) or ""
    short_doc = doc.split("\n")[0] if doc else ""

    return f"- `{func.__name__}({params_str}){ret}`: {short_doc}"


if __name__ == "__main__":
    # always target package at src.sap_functions
    generate_md_doc_for_codebase("src.sap_functions")
