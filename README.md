# WHP Language Data

Version-controlled language data and decoding tools for the World History Project.

## Decoder status

The first decoder stage is operational. It reads YAML language profiles and turns historical spellings into **traceable phonological candidates**. It does not silently claim a complete pronunciation or translation.

Current profile:

- Old Saxon (`profiles/old_saxon.yaml`)

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

The JSON format is the default and preserves every candidate, confidence label, note, normalization change, and warning:

```bash
python -m decoder.cli "heƀenrîki"
```

## Design rules

1. Preserve the original Unicode text.
2. Report normalization rather than hiding it.
3. Match longer graphemes first (`uu` before `u`).
4. Keep rival readings when context does not resolve them.
5. Separate orthography, phonology, morphology, semantics, chronology, and translation.
6. Attach provenance to language-profile claims.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Next stages

Context-sensitive sound rules, lexemes, morphology, manuscript variants, chronology filters, and ranked translation candidates can be added without replacing the profile format.
