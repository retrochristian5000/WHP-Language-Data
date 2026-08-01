# WHP Language Data

Version-controlled language data and decoding tools for the World History Project.

## Decoder status

The decoder reads YAML profiles and preserves a traceable chain from source script through historical orthography to broad phonological candidates. It does not silently claim a complete pronunciation or translation.

Language profiles:

- Old Saxon (`profiles/old_saxon.yaml`)
- Old High German (`profiles/old_high_german.yaml`)

Script profiles:

- Elder Futhark (`scripts/elder_futhark.yaml`)

## Install

```bash
python -m pip install -e .
```

## Decode Old Saxon

```bash
python -m decoder.cli --profile profiles/old_saxon.yaml --format text "thesa uuerold"
```

Example primary output:

```text
thesa -> θesa
uuerold -> werold
```

## Decode Old High German

```bash
python -m decoder.cli --profile profiles/old_high_german.yaml --format text "pfunt zunga uuort"
```

Example primary output:

```text
pfunt -> pfunt
zunga -> tsuŋga
uuort -> wort
```

The Old High German profile keeps dialect- and context-sensitive spellings such as `ph`, `zz`, `ch`, `th`, and `uu` as explicit candidate sets instead of flattening them into one standardized pronunciation.

## Decode Elder Futhark into Old Saxon

```bash
python -m decoder.cli \
  --script-profile scripts/elder_futhark.yaml \
  --profile profiles/old_saxon.yaml \
  --format text \
  "ᚦᛖᛋᚨ"
```

The pipeline preserves both stages:

```text
ᚦᛖᛋᚨ -> thesa
thesa -> θesa
```

Runic punctuation is normalized only as a reported script-level change:

```bash
python -m decoder.cli \
  --script-profile scripts/elder_futhark.yaml \
  --profile profiles/old_saxon.yaml \
  --format text \
  "ᚹᛟᚱᛞ᛫ᚠᛟᛚᚲ"
```

Primary transliteration:

```text
word folk
```

The Elder Futhark profile preserves uncertain readings such as `ᛇ -> ï | i | e` and `ᛉ -> z | ʀ | r`. It does not infer an inscription's language, date, bind-runes, damaged strokes, or word division beyond explicit separators.

The JSON format is the default and preserves every candidate, confidence label, note, normalization change, warning, script segment, and language segment:

```bash
python -m decoder.cli --profile profiles/old_saxon.yaml "heƀenrîki"
python -m decoder.cli --profile profiles/old_high_german.yaml "ezzan"
python -m decoder.cli --script-profile scripts/elder_futhark.yaml "ᛇ"
```

## Design rules

1. Preserve the original Unicode source text.
2. Report normalization rather than hiding it.
3. Match longer graphemes first (`uu` before `u`).
4. Keep rival readings when context does not resolve them.
5. Keep script transliteration separate from language phonology, morphology, semantics, chronology, and translation.
6. Do not infer language or chronology from script identity alone.
7. Attach provenance to profile claims.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Next stages

Context-sensitive sound rules, lexemes, morphology, manuscript and inscription variants, chronology filters, bind-rune handling, and ranked translation candidates can be added without replacing the profile format.
