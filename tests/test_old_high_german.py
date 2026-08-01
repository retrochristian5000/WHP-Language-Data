from pathlib import Path
import unittest

from decoder.engine import decode_text, load_profile

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "old_high_german.yaml"


class OldHighGermanDecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = load_profile(PROFILE)

    def test_longest_match_decodes_double_u_as_w(self) -> None:
        result = decode_text("uuort", self.profile)
        word = result["tokens"][0]
        self.assertEqual(word["segments"][0]["grapheme"], "uu")
        self.assertEqual(word["segments"][0]["candidates"][0]["value"], "w")
        self.assertEqual(word["primary_candidate"], "wort")

    def test_ph_retains_shifted_p_alternatives(self) -> None:
        result = decode_text("phunt", self.profile)
        segment = result["tokens"][0]["segments"][0]
        self.assertEqual(segment["grapheme"], "ph")
        self.assertEqual([item["value"] for item in segment["candidates"]], ["pf", "f"])
        self.assertEqual(result["tokens"][0]["primary_candidate"], "pfunt")

    def test_zz_retains_affricate_fricative_ambiguity(self) -> None:
        result = decode_text("ezzan", self.profile)
        segment = result["tokens"][0]["segments"][1]
        self.assertEqual(segment["grapheme"], "zz")
        self.assertEqual([item["value"] for item in segment["candidates"]], ["ts", "sː"])

    def test_ch_retains_dialect_and_position_ambiguity(self) -> None:
        result = decode_text("chind", self.profile)
        segment = result["tokens"][0]["segments"][0]
        self.assertEqual(segment["grapheme"], "ch")
        self.assertEqual([item["value"] for item in segment["candidates"]], ["x", "kx", "k"])

    def test_sample_words_have_no_unmapped_graphemes(self) -> None:
        result = decode_text("pfunt zunga uuort", self.profile)
        warnings = [
            warning
            for token in result["tokens"]
            if token["type"] == "word"
            for warning in token["warnings"]
        ]
        self.assertEqual(warnings, [])
        primaries = [
            token["primary_candidate"]
            for token in result["tokens"]
            if token["type"] == "word"
        ]
        self.assertEqual(primaries, ["pfunt", "tsuŋga", "wort"])


if __name__ == "__main__":
    unittest.main()
