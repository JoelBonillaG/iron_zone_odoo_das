#!/usr/bin/env python3
"""Lightweight repository validation for CI."""

from __future__ import annotations

import ast
import compileall
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON_DIRS = ("addons", "scripts", "seeds")
XML_DIRS = ("addons", "seeds")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_python() -> None:
    for directory in PYTHON_DIRS:
        path = ROOT / directory
        if path.exists() and not compileall.compile_dir(path, quiet=1):
            fail(f"Python syntax validation failed in {directory}")


def validate_manifests() -> None:
    manifests = sorted((ROOT / "addons").glob("*/__manifest__.py"))
    if not manifests:
        fail("No Odoo manifests found in addons/")

    required_keys = {"name", "version", "depends"}
    for manifest in manifests:
        try:
            data = ast.literal_eval(manifest.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            fail(f"Invalid manifest {manifest.relative_to(ROOT)}: {exc}")

        missing = required_keys.difference(data)
        if missing:
            fail(f"Manifest {manifest.relative_to(ROOT)} missing keys: {sorted(missing)}")

        if not isinstance(data.get("depends"), list):
            fail(f"Manifest {manifest.relative_to(ROOT)} depends must be a list")


def validate_xml() -> None:
    for directory in XML_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue

        for xml_file in sorted(base.rglob("*.xml")):
            try:
                ET.parse(xml_file)
            except ET.ParseError as exc:
                fail(f"Invalid XML {xml_file.relative_to(ROOT)}: {exc}")


def main() -> None:
    validate_python()
    validate_manifests()
    validate_xml()
    print("Repository validation passed.")


if __name__ == "__main__":
    main()
