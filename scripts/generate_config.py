#!/usr/bin/env python3
"""Render sanitized Junos configuration files from YAML inventory."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def load_inventory(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("devices"), dict):
        raise ValueError("Inventory must contain a top-level 'devices' mapping")
    return data["devices"]


def render_device(template_path: Path, device: dict[str, Any]) -> str:
    required = {"hostname", "router_id", "local_as", "neighbors"}
    missing = sorted(required.difference(device))
    if missing:
        raise ValueError(f"Device is missing required fields: {', '.join(missing)}")

    environment = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = environment.get_template(template_path.name)
    return template.render(**device)


def generate(inventory_path: Path, template_path: Path, output_dir: Path) -> list[Path]:
    devices = load_inventory(inventory_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for name, device in sorted(devices.items()):
        if not isinstance(device, dict):
            raise ValueError(f"Device '{name}' must be a mapping")
        rendered = render_device(template_path, device)
        destination = output_dir / f"{name}.conf"
        destination.write_text(rendered, encoding="utf-8")
        written.append(destination)

    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        written = generate(args.inventory, args.template, args.output_dir)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}")
        return 2

    for path in written:
        print(f"generated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
