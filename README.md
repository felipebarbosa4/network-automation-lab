# Network Automation Lab

[![CI](https://github.com/felipebarbosa4/network-automation-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/felipebarbosa4/network-automation-lab/actions/workflows/ci.yml)

A public, sanitized portfolio of network automation patterns for configuration generation, validation, and operational troubleshooting.

> All device names, addresses, credentials, and outputs in this repository are fictional lab data. Nothing here should be applied to a production network without review, testing, change control, and rollback planning.

## What this repository demonstrates

- Data-driven generation of Junos configuration snippets with Jinja2
- Offline validation of expected BGP state from structured command output
- Safe comparison of intended and observed configuration text
- Small, testable Python tools with no live-device access by default
- CI checks that run without secrets or external infrastructure

## Repository layout

```text
.
├── inventory/
│   └── lab-devices.yaml
├── sample-data/
│   ├── bgp-healthy.json
│   └── bgp-unhealthy.json
├── scripts/
│   ├── compare_config.py
│   ├── generate_config.py
│   └── validate_bgp.py
├── templates/
│   └── junos_bgp.j2
├── tests/
│   └── test_tools.py
├── .github/workflows/ci.yml
├── requirements.txt
└── SECURITY.md
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
pytest -q
```

Generate configuration from the sample inventory:

```bash
python scripts/generate_config.py \
  --inventory inventory/lab-devices.yaml \
  --template templates/junos_bgp.j2 \
  --output-dir generated
```

Validate a healthy sample:

```bash
python scripts/validate_bgp.py \
  --input sample-data/bgp-healthy.json \
  --expected inventory/lab-devices.yaml \
  --device ott-pe-01
```

Compare two configuration files:

```bash
python scripts/compare_config.py intended.conf observed.conf
```

## Design principles

1. **Offline first:** examples operate on files, not production equipment.
2. **Fail clearly:** validation exits non-zero and prints actionable differences.
3. **Separate data from logic:** inventory, templates, and code remain independent.
4. **Test deterministic behaviour:** CI does not depend on reachable devices.
5. **Sanitize everything:** examples use documentation address ranges and fictional names.

## Roadmap

- Add lab-only NETCONF collection examples with explicit safeguards
- Add pre-change and post-change validation reports
- Add EVPN and MPLS operational-state parsers
- Add inventory schema validation

## License

MIT. See [LICENSE](LICENSE).
