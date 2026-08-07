#!/usr/bin/env python3
"""Classify Mihomo proxy names offline without contacting providers or node IPs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REGIONS = (
    ("US", (r"(?:美国|美國|los angeles|san jose|seattle|new york|dallas)", r"(?:\bUS\b|\bUSA\b|united states|america)", "🇺🇸")),
    ("JP", (r"(?:日本|东京|東京|大阪|埼玉)", r"(?:\bJP\b|japan|tokyo|osaka)", "🇯🇵")),
    ("HK", (r"(?:香港)", r"(?:\bHK\b|hong kong|hkg)", "🇭🇰")),
    ("SG", (r"(?:新加坡|獅城|狮城)", r"(?:\bSG\b|singapore)", "🇸🇬")),
)
TAG_PATTERNS = (
    ("AI", r"(?:\bAI\b|GPT|ChatGPT|Claude|Gemini|OpenAI|人工智能|优化)"),
    ("GPT", r"(?:GPT|ChatGPT)"),
    ("Streaming", r"(?:Netflix|Disney|HBO|Spotify|Twitch|流媒体|串流)"),
    ("Netflix", r"Netflix"),
    ("Japan", r"(?:日本|东京|東京|大阪|埼玉|\bJP\b|Japan|Tokyo|Osaka|IIJ)"),
    ("Media", r"(?:IIJ|日本音乐|日音|动画|動漫|票务|票務|Media)"),
    ("Premium", r"(?:Premium|优化|優化|专线|專線|IEPL|IPLC)"),
)


def extract_names(text: str) -> list[str]:
    """Extract standard YAML proxy `name` values without parsing executable YAML features."""
    names: list[str] = []
    for raw in text.splitlines():
        match = re.match(r"^\s*(?:-\s+)?name\s*:\s*(.+?)\s*$", raw)
        if not match:
            continue
        value = match.group(1).strip().strip("\"'")
        if value:
            names.append(value)
    return names


def classify(name: str) -> tuple[str | None, list[str]]:
    # Precedence: Chinese/city name, English name, emoji. Unknown is intentionally left unset.
    region = None
    for code, (chinese, english, emoji) in REGIONS:
        if re.search(chinese, name, re.I):
            region = code
            break
        if re.search(english, name, re.I):
            region = code
            break
        if emoji in name:
            region = code
            break
    tags = [tag for tag, pattern in TAG_PATTERNS if re.search(pattern, name, re.I)]
    if "Netflix" in tags and "Streaming" not in tags:
        tags.insert(0, "Streaming")
    if "Japan" in tags and "Media" not in tags and "IIJ" in name:
        tags.append("Media")
    return region, tags


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="local Mihomo subscription YAML")
    parser.add_argument("--output", type=Path, default=Path("node-classification.yaml"))
    args = parser.parse_args()

    names = extract_names(args.input.read_text(encoding="utf-8"))
    lines = ["# Generated offline. Unknown nodes must remain in the default selector.", "nodes:"]
    for name in names:
        region, tags = classify(name)
        lines.append(f"  - name: {yaml_quote(name)}")
        lines.append(f"    region: {region if region else 'UNKNOWN'}")
        lines.append("    tags: [" + ", ".join(tags) + "]")
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Classified {len(names)} nodes into {args.output}")


if __name__ == "__main__":
    main()
