#!/usr/bin/env python3
"""Static validation for Shadowrocket, Mihomo providers, and route expectations."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "shadowrocket-ai.conf"
TEMPLATE = ROOT / "templates" / "config-template.yaml"
RULE_FILES = sorted((ROOT / "rules").rglob("*.list"))
PROVIDER_FILES = sorted((ROOT / "providers").glob("*.yaml"))
SPECIAL_POLICIES = {"DIRECT", "REJECT", "REJECT-DROP", "REJECT-TINYGIF", "REJECT-DICT"}
ALLOWED_RULE_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-ASN", "USER-AGENT", "RULE-SET", "DOMAIN-SET", "GEOIP", "FINAL", "MATCH"}
DOMAIN_RULE_TYPES = {"DOMAIN", "DOMAIN-SUFFIX"}
EXPECTED_TEMPLATE_GROUPS = {"🚀节点选择", "♻️自动选择", "🛑故障转移", "🇺🇸 US", "🇯🇵 JP", "🇭🇰 HK", "🇸🇬 SG", "🤖 AI", "🌐 Google", "📺 YouTube", "🐱 GitHub", "👨‍💻 Developer", "🎬 Netflix", "🎵 Spotify", "🇯🇵 Japan-Media", "🍎 Apple", "💰 Finance", "💳 Payment"}
PRIORITY = ["LAN", "Advertising", "Malware", "Finance", "Payment", "Apple", "OpenAI", "Claude", "GoogleAI", "AI-Platform", "AI-Image", "AI-Model", "Google", "YouTube", "GitHub", "Copilot", "Developer", "Netflix", "DisneyPlus", "Spotify", "Twitch", "Japan-Media", "Telegram", "X", "Instagram", "Facebook", "Microsoft", "China"]
ROUTE_CASES = {
    "chatgpt.com": "🤖 AI",
    "platform.openai.com": "🤖 AI",
    "gemini.google.com": "🤖 AI",
    "youtube.com": "📺 YouTube",
    "netflix.com": "🎬 Netflix",
    "github.com": "🐱 GitHub",
    "icloud.com": "🍎 Apple",
    "eplus.jp": "🇯🇵 Japan-Media",
    "icbc.com.cn": "💰 Finance",
    "alipay.com": "💳 Payment",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def active_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]


def validate_domain(value: str, context: str) -> None:
    if value in {"localhost", "local"}:
        return
    if len(value) > 253 or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", value):
        fail(f"{context}: invalid ASCII domain {value!r}")
    if ".." in value or "." not in value:
        fail(f"{context}: invalid domain label structure {value!r}")


def validate_rule(line: str, context: str, *, provider: bool = False) -> None:
    parts = [part.strip() for part in line.split(",")]
    if parts[0] not in ALLOWED_RULE_TYPES:
        fail(f"{context}: unsupported rule type {parts[0]!r}")
    if len(parts) < 2:
        fail(f"{context}: malformed rule")
    if provider and parts[0] in {"RULE-SET", "FINAL", "MATCH"}:
        fail(f"{context}: {parts[0]} is not valid in a classical Rule Provider")
    if parts[0] in DOMAIN_RULE_TYPES:
        validate_domain(parts[1], context)
    if parts[0] == "DOMAIN-KEYWORD" and parts[1].lower() in {"bank", "payment", "china"}:
        fail(f"{context}: unsafe broad keyword {parts[1]!r}")


def validate_config(text: str) -> None:
    for required in ("[General]", "[Proxy Group]", "[Rule]"):
        if required not in text:
            fail(f"missing required section: {required}")
    if "bypass-tun" in text:
        fail("deprecated/non-canonical field bypass-tun found; use tun-excluded-routes")
    if "[MITM]" in text or "[URL Rewrite]" in text:
        fail("MITM and URL Rewrite sections must not be enabled in this repository")
    if re.search(r"(?i)(?:subscribe\?|token=|password=|uuid=|private[-_ ]?key|client_secret)", text):
        fail("possible sensitive value found in configuration")

    proxy_section = text.split("[Proxy Group]", 1)[1].split("[Rule]", 1)[0]
    groups = {line.split("=", 1)[0].strip() for line in proxy_section.splitlines() if line.strip() and not line.lstrip().startswith("#") and "=" in line}
    if not groups:
        fail("no proxy groups found")
    if "DIRECT" not in {part.strip() for part in next(line for line in proxy_section.splitlines() if line.startswith("Spotify =")).split("=", 1)[1].split(",")}:
        fail("Spotify proxy group must include DIRECT")

    active_rules = active_lines(CONFIG)[active_lines(CONFIG).index("[Rule]") + 1 :]
    if not active_rules or active_rules[-1] != "FINAL,节点选择":
        fail("the final active rule must be exactly FINAL,节点选择")
    if sum(line.startswith("FINAL,") for line in active_rules) != 1:
        fail("configuration must contain exactly one FINAL rule")
    duplicates = {line for line in active_rules if active_rules.count(line) > 1}
    if duplicates:
        fail(f"duplicate active rules found: {', '.join(sorted(duplicates))}")
    for line in active_rules:
        validate_rule(line, "shadowrocket-ai.conf")
        parts = [part.strip() for part in line.split(",")]
        if parts[0] == "RULE-SET":
            if len(parts) != 3 or not parts[1].startswith("https://"):
                fail(f"malformed RULE-SET: {line}")
            target = parts[2]
        elif parts[0] == "FINAL":
            target = parts[1]
        elif len(parts) >= 3:
            target = parts[2]
        else:
            continue
        if target not in groups and target not in SPECIAL_POLICIES:
            fail(f"rule references unknown policy {target!r}: {line}")

    for narrow, broad, message in (("Gemini/Gemini.list", "Google/Google.list", "Gemini rules must appear before broad Google rules"), ("Copilot/Copilot.list", "Microsoft/Microsoft.list", "Copilot rules must appear before broad Microsoft rules")):
        if text.find(narrow) < 0 or text.find(broad) < 0 or text.find(narrow) > text.find(broad):
            fail(message)


def validate_rule_files() -> None:
    if not RULE_FILES:
        fail("no local rule files found")
    for path in RULE_FILES:
        for number, line in enumerate(active_lines(path), start=1):
            validate_rule(line, f"{path.relative_to(ROOT)}:{number}")


def provider_rules(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not any(line == "behavior: classical" for line in lines):
        fail(f"{path.relative_to(ROOT)}: missing behavior: classical")
    try:
        start = lines.index("payload:")
    except ValueError:
        fail(f"{path.relative_to(ROOT)}: missing payload")
    rules = [line.removeprefix("  - ").strip() for line in lines[start + 1 :] if line.startswith("  - ")]
    return rules


def validate_providers() -> dict[str, list[str]]:
    if len(PROVIDER_FILES) < 28:
        fail("missing generated Mihomo Rule Providers")
    result: dict[str, list[str]] = {}
    for path in PROVIDER_FILES:
        rules = provider_rules(path)
        duplicates = {rule for rule in rules if rules.count(rule) > 1}
        if duplicates:
            fail(f"{path.relative_to(ROOT)}: duplicate payload rules: {', '.join(sorted(duplicates))}")
        for number, rule in enumerate(rules, start=1):
            validate_rule(rule, f"{path.relative_to(ROOT)}:{number}", provider=True)
        result[path.stem] = rules
    return result


def validate_template(provider_payloads: dict[str, list[str]]) -> None:
    if not TEMPLATE.exists():
        fail("templates/config-template.yaml not found")
    text = TEMPLATE.read_text(encoding="utf-8")
    if re.search(r"(?i)(?:token=|password=|uuid=|private[-_ ]?key)", text):
        fail("possible sensitive value found in Mihomo template")
    groups = set(re.findall(r"^  - name: (.+)$", text, re.M))
    missing_groups = EXPECTED_TEMPLATE_GROUPS - groups
    if missing_groups:
        fail(f"Mihomo template missing groups: {', '.join(sorted(missing_groups))}")
    provider_names = set(re.findall(r"^  ([A-Za-z0-9-]+): \{type: file, behavior: classical, path: \./providers/([A-Za-z0-9-]+)\.yaml\}$", text, re.M))
    for name, file_stem in provider_names:
        if name != file_stem or name not in provider_payloads:
            fail(f"Mihomo template references missing provider {name}")
    if len(provider_names) < 28:
        fail("Mihomo template must reference all generated providers")
    rule_lines = re.findall(r"^  - RULE-SET,([^,]+),(.+)$", text, re.M)
    names = [name for name, _ in rule_lines]
    positions = {name: names.index(name) for name in names}
    for name in PRIORITY:
        if name not in positions:
            fail(f"Mihomo template missing priority rule {name}")
    if any(positions[left] >= positions[right] for left, right in zip(PRIORITY, PRIORITY[1:])):
        fail("Mihomo template Rule Provider order violates required priority")
    for domain, expected_policy in ROUTE_CASES.items():
        actual_policy = None
        for provider, policy in rule_lines:
            for rule in provider_payloads[provider]:
                kind, value, *_ = rule.split(",")
                if kind == "DOMAIN" and domain == value or kind == "DOMAIN-SUFFIX" and (domain == value or domain.endswith("." + value)):
                    actual_policy = policy
                    break
            if actual_policy:
                break
        if actual_policy != expected_policy:
            fail(f"route simulation {domain}: expected {expected_policy}, got {actual_policy}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shadowrocket-only", action="store_true")
    args = parser.parse_args()
    if not CONFIG.exists():
        fail("shadowrocket-ai.conf not found")
    validate_config(CONFIG.read_text(encoding="utf-8"))
    validate_rule_files()
    if args.shadowrocket_only:
        print(f"Validated Shadowrocket configuration and {len(RULE_FILES)} local rule files.")
        return
    provider_payloads = validate_providers()
    validate_template(provider_payloads)
    print(f"Validated Shadowrocket, {len(RULE_FILES)} local rule files, {len(PROVIDER_FILES)} Mihomo Rule Providers, template order, and {len(ROUTE_CASES)} route simulations.")


if __name__ == "__main__":
    main()
