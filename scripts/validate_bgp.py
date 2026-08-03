#!/usr/bin/env python3
"""Validate offline BGP state against expectations in the lab inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def validate(state: dict[str, Any], inventory: dict[str, Any], device_name: str) -> list[str]:
    devices = inventory.get("devices")
    if not isinstance(devices, dict) or device_name not in devices:
        return [f"device '{device_name}' is missing from inventory"]

    device = devices[device_name]
    expected_neighbors = device.get("neighbors", [])
    observed_neighbors = state.get("neighbors", [])
    observed_by_address = {
        item.get("address"): item
        for item in observed_neighbors
        if isinstance(item, dict) and item.get("address")
    }

    failures: list[str] = []
    for expected in expected_neighbors:
        address = expected["address"]
        observed = observed_by_address.get(address)
        if observed is None:
            failures.append(f"{address}: neighbor missing from observed state")
            continue

        if observed.get("state") != "Established":
            failures.append(f"{address}: state is {observed.get('state')!r}, expected 'Established'")
        if int(observed.get("peer_as", -1)) != int(expected["peer_as"]):
            failures.append(
                f"{address}: peer AS is {observed.get('peer_as')!r}, expected {expected['peer_as']}"
            )

        received = int(observed.get("received_prefixes", 0))
        minimum = int(expected.get("min_received_prefixes", 0))
        if received < minimum:
            failures.append(f"{address}: received {received} prefixes, expected at least {minimum}")

    expected_addresses = {item["address"] for item in expected_neighbors}
    unexpected = sorted(set(observed_by_address).difference(expected_addresses))
    for address in unexpected:
        failures.append(f"{address}: unexpected observed neighbor")

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Observed BGP JSON")
    parser.add_argument("--expected", type=Path, required=True, help="Inventory YAML")
    parser.add_argument("--device", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        state = load_json(args.input)
        inventory = load_yaml(args.expected)
        failures = validate(state, inventory, args.device)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}")
        return 2

    if failures:
        print(f"BGP validation FAILED for {args.device}")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"BGP validation PASSED for {args.device}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
