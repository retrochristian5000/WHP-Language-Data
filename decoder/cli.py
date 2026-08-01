"""CLI for the WHP language decoder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .engine import DecodeError, decode_text, load_profile


def _render_segments(lines: list[str], tokens: list[dict[str, Any]]) -> None:
    for token in tokens:
        if token["type"] != "word":
            continue
        lines.append(f"{token['text']} -> {token['primary_candidate']}")
        for segment in token["segments"]:
            values = ", ".join(str(item["value"]) for item in segment["candidates"])
            note = f" — {segment['note']}" if segment.get("note") else ""
            lines.append(f"  {segment['grapheme']}: {values}{note}")
        for warning in token["warnings"]:
            lines.append(f"  WARNING: {warning}")


def _render_text(result: dict[str, Any]) -> str:
    lines: list[str] = []
    script = result.get("script_decoding")
    if script:
        lines.extend([
            f"Script: {script['script']['name']}",
            f"Script normalized: {script['normalized']}",
            f"Transliteration: {script['primary_transliteration']}",
            "",
            "Script decoding:",
        ])
        _render_segments(lines, script["tokens"])
        lines.extend(["", "Language decoding:"])

    lines.extend([f"Language: {result['language']['name']}", f"Normalized: {result['normalized']}", ""])
    _render_segments(lines, result["tokens"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decode historical scripts and orthographies with YAML profiles.")
    parser.add_argument("text", nargs="?", help="Text to decode; stdin when omitted.")
    parser.add_argument("--profile", default=str(Path("profiles") / "old_saxon.yaml"))
    parser.add_argument("--script-profile", help="Optional script-transliteration YAML profile.")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()
    try:
        language_profile = load_profile(args.profile)
        script_profile = load_profile(args.script_profile) if args.script_profile else None
        result = decode_text(text, language_profile, script_profile=script_profile)
    except DecodeError as exc:
        print(f"decoder error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json" else _render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
