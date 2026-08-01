"""CLI for the WHP language decoder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .engine import DecodeError, decode_text, load_profile


def _render_text(result: dict[str, Any]) -> str:
    lines = [f"Language: {result['language']['name']}", f"Normalized: {result['normalized']}", ""]
    for token in result["tokens"]:
        if token["type"] != "word":
            continue
        lines.append(f"{token['text']} -> {token['primary_candidate']}")
        for segment in token["segments"]:
            values = ", ".join(str(item["value"]) for item in segment["candidates"])
            note = f" — {segment['note']}" if segment.get("note") else ""
            lines.append(f"  {segment['grapheme']}: {values}{note}")
        for warning in token["warnings"]:
            lines.append(f"  WARNING: {warning}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decode historical orthography with a YAML profile.")
    parser.add_argument("text", nargs="?", help="Text to decode; stdin when omitted.")
    parser.add_argument("--profile", default=str(Path("profiles") / "old_saxon.yaml"))
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()
    try:
        result = decode_text(text, load_profile(args.profile))
    except DecodeError as exc:
        print(f"decoder error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json" else _render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
