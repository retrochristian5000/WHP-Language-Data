"""Conservative YAML-profile decoding primitives."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
import unicodedata

import yaml


class DecodeError(ValueError):
    """Raised when a profile or decoding request is invalid."""


@dataclass(frozen=True)
class CompiledRule:
    grapheme: str
    candidates: tuple[dict[str, Any], ...]
    note: str | None = None


def load_profile(path: str | Path) -> dict[str, Any]:
    """Load and minimally validate a YAML language profile."""
    profile_path = Path(path)
    try:
        with profile_path.open("r", encoding="utf-8") as handle:
            profile = yaml.safe_load(handle)
    except OSError as exc:
        raise DecodeError(f"Could not read profile {profile_path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise DecodeError(f"Invalid YAML in {profile_path}: {exc}") from exc

    if not isinstance(profile, dict):
        raise DecodeError("Profile root must be a mapping.")

    for required in (("profile", "id"), ("profile", "name"), ("normalization", "unicode_form"), ("decoder", "graphemes")):
        value: Any = profile
        for part in required:
            if not isinstance(value, dict) or part not in value:
                raise DecodeError(f"Profile is missing required field: {'.'.join(required)}")
            value = value[part]

    graphemes = profile["decoder"]["graphemes"]
    if not isinstance(graphemes, dict) or not graphemes:
        raise DecodeError("decoder.graphemes must be a non-empty mapping.")
    return profile


def _normalize(text: str, profile: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    settings = profile["normalization"]
    normalized = unicodedata.normalize(settings.get("unicode_form", "NFC"), text)
    changes: list[dict[str, str]] = []

    for item in settings.get("replacements", []):
        if not isinstance(item, dict) or "from" not in item or "to" not in item:
            raise DecodeError("Each normalization replacement needs 'from' and 'to'.")
        source, target = str(item["from"]), str(item["to"])
        if source in normalized:
            normalized = normalized.replace(source, target)
            changes.append({"from": source, "to": target, "reason": str(item.get("reason", "profile replacement"))})

    if settings.get("casefold", True):
        casefolded = normalized.casefold()
        if casefolded != normalized:
            changes.append({"from": normalized, "to": casefolded, "reason": "Unicode casefold"})
        normalized = casefolded
    return normalized, changes


def _word_tokens(text: str) -> Iterable[tuple[str, bool]]:
    current: list[str] = []
    current_is_word: bool | None = None

    def is_word_char(char: str) -> bool:
        return unicodedata.category(char)[0] in {"L", "M", "N"} or char in {"'", "’", "-"}

    for char in text:
        word_char = is_word_char(char)
        if current_is_word is None or word_char == current_is_word:
            current.append(char)
            current_is_word = word_char
        else:
            yield "".join(current), bool(current_is_word)
            current, current_is_word = [char], word_char
    if current:
        yield "".join(current), bool(current_is_word)


def _compile_rules(profile: dict[str, Any]) -> list[CompiledRule]:
    rules: list[CompiledRule] = []
    for grapheme, spec in profile["decoder"]["graphemes"].items():
        if isinstance(spec, str):
            candidates, note = ({"value": spec, "confidence": "unspecified"},), None
        elif isinstance(spec, dict):
            raw_candidates = spec.get("candidates", [])
            if not isinstance(raw_candidates, list) or not raw_candidates:
                raise DecodeError(f"Grapheme {grapheme!r} needs at least one candidate.")
            candidates = tuple(candidate if isinstance(candidate, dict) else {"value": str(candidate), "confidence": "unspecified"} for candidate in raw_candidates)
            note = str(spec["note"]) if "note" in spec else None
        else:
            raise DecodeError(f"Invalid rule for grapheme {grapheme!r}.")
        rules.append(CompiledRule(str(grapheme), candidates, note))
    return sorted(rules, key=lambda rule: (-len(rule.grapheme), rule.grapheme))


def _decode_word(word: str, rules: list[CompiledRule]) -> dict[str, Any]:
    cursor = 0
    segments: list[dict[str, Any]] = []
    warnings: list[str] = []
    while cursor < len(word):
        match = next((rule for rule in rules if word.startswith(rule.grapheme, cursor)), None)
        if match is None:
            char = word[cursor]
            segments.append({"grapheme": char, "span": [cursor, cursor + 1], "candidates": [{"value": char, "confidence": "unknown"}], "status": "unmapped"})
            warnings.append(f"No profile rule for {char!r} at offset {cursor}.")
            cursor += 1
            continue
        segment: dict[str, Any] = {"grapheme": match.grapheme, "span": [cursor, cursor + len(match.grapheme)], "candidates": list(match.candidates), "status": "mapped"}
        if match.note:
            segment["note"] = match.note
        segments.append(segment)
        cursor += len(match.grapheme)
    primary = "".join(str(segment["candidates"][0]["value"]) for segment in segments)
    return {"text": word, "segments": segments, "primary_candidate": primary, "warnings": warnings}


def decode_text(text: str, profile: dict[str, Any]) -> dict[str, Any]:
    """Decode text with grapheme-level provenance."""
    if not isinstance(text, str) or not text:
        raise DecodeError("Input text must be a non-empty string.")
    normalized, changes = _normalize(text, profile)
    rules = _compile_rules(profile)
    tokens: list[dict[str, Any]] = []
    for token, is_word in _word_tokens(normalized):
        if is_word:
            decoded = _decode_word(token, rules)
            decoded["type"] = "word"
            tokens.append(decoded)
        else:
            tokens.append({"text": token, "type": "separator"})
    return {"decoder_version": "0.1.0", "stage": "orthography_to_phonological_candidates", "language": profile["profile"], "input": text, "normalized": normalized, "normalization_changes": changes, "tokens": tokens, "limitations": profile.get("limitations", [])}
