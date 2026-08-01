from pathlib import Path
import unittest

from decoder.engine import decode_text, load_profile

ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_PROFILE = ROOT / "profiles" / "old_saxon.yaml"
SCRIPT_PROFILE = ROOT / "scripts" / "elder_futhark.yaml"


class ElderFutharkDecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.language = load_profile(LANGUAGE_PROFILE)
        cls.script = load_profile(SCRIPT_PROFILE)

    def test_runic_text_transliterates_before_language_decoding(self) -> None:
        result = decode_text("ᚦᛖᛋᚨ", self.language, script_profile=self.script)
        self.assertEqual(result["input"], "ᚦᛖᛋᚨ")
        self.assertEqual(result["language_input"], "thesa")
        self.assertEqual(result["script_decoding"]["primary_transliteration"], "thesa")
        self.assertEqual(result["tokens"][0]["primary_candidate"], "θesa")

    def test_runic_punctuation_is_reported_and_becomes_word_space(self) -> None:
        result = decode_text("ᚹᛟᚱᛞ᛫ᚠᛟᛚᚲ", self.language, script_profile=self.script)
        self.assertEqual(result["language_input"], "word folk")
        self.assertEqual(result["script_decoding"]["normalized"], "ᚹᛟᚱᛞ ᚠᛟᛚᚲ")
        self.assertTrue(result["script_decoding"]["normalization_changes"])

    def test_eihwaz_ambiguity_is_retained(self) -> None:
        result = decode_text("ᛇ", self.language, script_profile=self.script)
        segment = result["script_decoding"]["tokens"][0]["segments"][0]
        self.assertEqual([item["value"] for item in segment["candidates"]], ["ï", "i", "e"])

    def test_graphic_variants_remain_distinct_source_graphemes(self) -> None:
        result = decode_text("ᚻᛋᛝ", self.language, script_profile=self.script)
        segments = result["script_decoding"]["tokens"][0]["segments"]
        self.assertEqual([segment["grapheme"] for segment in segments], ["ᚻ", "ᛋ", "ᛝ"])
        self.assertEqual(result["language_input"], "hsng")

    def test_language_only_mode_remains_backward_compatible(self) -> None:
        result = decode_text("thesa", self.language)
        self.assertNotIn("script_decoding", result)
        self.assertNotIn("language_input", result)
        self.assertEqual(result["tokens"][0]["primary_candidate"], "θesa")


if __name__ == "__main__":
    unittest.main()
