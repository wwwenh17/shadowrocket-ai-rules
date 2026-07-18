#!/usr/bin/env python3
"""Conservative static checks for the Shadowrocket configuration and local rules."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "shadowrocket-ai.conf"
RULE_FILES = sorted((ROOT / "rules").glob("*.list"))

ALLOWED_RULE_TYPES = {
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "IP-CIDR",
    "IP-ASN",
    "USER-AGENT",
    "RULE-SET",
    "DOMAIN-SET",
    "GEOIP",
    "FINAL",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_config(text: str) -> None:
    for required in ("[General]", "[Proxy Group]", "[Rule]"):
        if required not in text:
            fail(f"missing required section: {required}")

    if "bypass-tun" in text:
        fail("deprecated/non-canonical field bypass-tun found; use tun-excluded-routes")

    if re.search(r"^.*=\s*(?:url-test|select|fallback|load-balance|random).*\buse=true\b", text, re.M):
        fail("use=true found; this repository intentionally avoids it unless a subscription name is explicit")

    rule_section = text.split("[Rule]", 1)[1]
    active_rules = [
        line.strip()
        for line in rule_section.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not active_rules or not active_rules[-1].startswith("FINAL,"):
        fail("the final active rule must be FINAL")

    google_ai_pos = text.find("Gemini/Gemini.list")
    google_pos = text.find("Google/Google.list")
    if google_ai_pos < 0 or google_pos < 0 or google_ai_pos > google_pos:
        fail("Gemini rules must appear before broad Google rules")


def validate_rule_file(path: Path) -> None:
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",")]
        if parts[0] not in ALLOWED_RULE_TYPES:
            fail(f"{path}:{number}: unsupported rule type {parts[0]!r}")
        if len(parts) < 2:
            fail(f"{path}:{number}: malformed rule")


def main() -> None:
    if not CONFIG.exists():
        fail("shadowrocket-ai.conf not found")
    validate_config(CONFIG.read_text(encoding="utf-8"))
    if not RULE_FILES:
        fail("no local rule files found")
    for path in RULE_FILES:
        validate_rule_file(path)
    print(f"Validated {CONFIG.name} and {len(RULE_FILES)} local rule files.")


if __name__ == "__main__":
    main()
