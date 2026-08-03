from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_generate_config(tmp_path: Path) -> None:
    result = run(
        "scripts/generate_config.py",
        "--inventory",
        "inventory/lab-devices.yaml",
        "--template",
        "templates/junos_bgp.j2",
        "--output-dir",
        str(tmp_path),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    generated = (tmp_path / "ott-pe-01.conf").read_text(encoding="utf-8")
    assert "host-name ott-pe-01;" in generated
    assert "neighbor 192.0.2.2;" in generated
    assert "peer-as 64513;" in generated


def test_healthy_bgp_state_passes() -> None:
    result = run(
        "scripts/validate_bgp.py",
        "--input",
        "sample-data/bgp-healthy.json",
        "--expected",
        "inventory/lab-devices.yaml",
        "--device",
        "ott-pe-01",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASSED" in result.stdout


def test_unhealthy_bgp_state_fails() -> None:
    result = run(
        "scripts/validate_bgp.py",
        "--input",
        "sample-data/bgp-unhealthy.json",
        "--expected",
        "inventory/lab-devices.yaml",
        "--device",
        "ott-pe-01",
    )
    assert result.returncode == 1
    assert "FAILED" in result.stdout
    assert "Active" in result.stdout


def test_compare_config(tmp_path: Path) -> None:
    expected = tmp_path / "expected.conf"
    observed = tmp_path / "observed.conf"
    expected.write_text("system {\n host-name lab;\n}\n", encoding="utf-8")
    observed.write_text("\n# comment\nsystem {\n host-name lab; \n}\n", encoding="utf-8")

    result = run("scripts/compare_config.py", str(expected), str(observed))
    assert result.returncode == 0, result.stdout + result.stderr
