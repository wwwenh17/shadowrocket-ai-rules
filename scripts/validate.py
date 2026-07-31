#!/usr/bin/env python3
"""Conservative static checks for the Shadowrocket configuration and local rules."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "shadowrocket-ai.conf"
RULE_FILES = sorted((ROOT / "rules").glob("*.list"))
SPECIAL_POLICIES = {"DIRECT", "REJECT", "REJECT-DROP", "REJECT-TINYGIF", "REJECT-DICT"}
LOWERTOP_GENERAL_KEYS = {
    "tun-excluded-routes",
    "dns-server",
    "fallback-dns-server",
    "ipv6",
    "prefer-ipv6",
    "dns-direct-system",
    "dns-direct-fallback-proxy",
    "private-ip-answer",
    "icmp-auto-reply",
    "hijack-dns",
    "udp-policy-not-supported-behaviour",
}

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

    if "[MITM]" in text or "[URL Rewrite]" in text:
        fail("MITM and URL Rewrite sections must not be enabled in this repository")

    if re.search(r"(?i)(?:subscribe\?|token=|password=|uuid=|private[-_ ]?key|client_secret)", text):
        fail("possible sensitive value found in configuration")

    proxy_section = text.split("[Proxy Group]", 1)[1].split("[Rule]", 1)[0]
    groups = {
        line.split("=", 1)[0].strip()
        for line in proxy_section.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }
    if not groups:
        fail("no proxy groups found")

    rule_section = text.split("[Rule]", 1)[1]
    active_rules = [
        line.strip()
        for line in rule_section.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not active_rules or not active_rules[-1].startswith("FINAL,"):
        fail("the final active rule must be FINAL")

    finals = [line for line in active_rules if line.startswith("FINAL,")]
    if finals != ["FINAL,节点选择"]:
        fail("configuration must contain exactly one FINAL,节点选择 rule")

    duplicates = {line for line in active_rules if active_rules.count(line) > 1}
    if duplicates:
        fail(f"duplicate active rules found: {', '.join(sorted(duplicates))}")

    for line in active_rules:
        parts = [part.strip() for part in line.split(",")]
        if parts[0] not in ALLOWED_RULE_TYPES:
            fail(f"unsupported config rule type: {parts[0]!r}")
        if parts[0] == "RULE-SET":
            if len(parts) != 3 or not parts[1].startswith("https://"):
                fail(f"malformed RULE-SET: {line}")
            target = parts[2]
        elif parts[0] == "FINAL":
            target = parts[1] if len(parts) == 2 else ""
        elif len(parts) >= 3:
            target = parts[2]
        else:
            continue
        if target not in groups and target not in SPECIAL_POLICIES:
            fail(f"rule references unknown policy {target!r}: {line}")

    for narrow, broad, message in (
        ("Gemini/Gemini.list", "Google/Google.list", "Gemini rules must appear before broad Google rules"),
        ("Copilot/Copilot.list", "Microsoft/Microsoft.list", "Copilot rules must appear before broad Microsoft rules"),
    ):
        if text.find(narrow) < 0 or text.find(broad) < 0 or text.find(narrow) > text.find(broad):
            fail(message)


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


def validate_lowertop_reference(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for required in ("[General]", "[Proxy Group]", "[Rule]"):
        if required not in text:
            fail(f"LOWERTOP reference missing section: {required}")

    general = text.split("[General]", 1)[1].split("[Proxy", 1)[0]
    reference_keys = {
        line.split("=", 1)[0].strip()
        for line in general.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }
    missing = LOWERTOP_GENERAL_KEYS - reference_keys
    if missing:
        fail(f"LOWERTOP reference no longer exposes expected keys: {', '.join(sorted(missing))}")
    if "policy-regex-filter" not in text or "RULE-SET" not in text:
        fail("LOWERTOP reference no longer exposes expected rule or group syntax")
    print(f"Validated LOWERTOP reference compatibility: {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lowertop-reference", type=Path)
    args = parser.parse_args()

    if not CONFIG.exists():
        fail("shadowrocket-ai.conf not found")
    validate_config(CONFIG.read_text(encoding="utf-8"))
    if not RULE_FILES:
        fail("no local rule files found")
    for path in RULE_FILES:
        validate_rule_file(path)
    print(f"Validated {CONFIG.name} and {len(RULE_FILES)} local rule files.")
    if args.lowertop_reference:
        validate_lowertop_reference(args.lowertop_reference)


if __name__ == "__main__":
    main()
