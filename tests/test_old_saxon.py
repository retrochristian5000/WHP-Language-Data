from pathlib import Path
import unittest

from decoder.engine import decode_text, load_profile

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "old_saxon.yaml"


class OldSaxonDecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = load_profile(PROFILE)

    def test_longest_match_decodes_double_u_as_w(self) -> None:
        result = decode_text("uuerold", self.profile)
        word = result["tokens"][0]
        self.assertEqual(word["segments"][0]["grapheme"], "uu")
        self.assertEqual(word["segments"][0]["candidates"][0]["value"], "w")
        self.assertEqual(word["primary_candidate"], "werold")

    def test_th_retains_voicing_ambiguity(self) -> None:
        result = decode_text("thesa", self.profile)
        values = [item["value"] for item in result["tokens"][0]["segments"][0]["candidates"]]
        self.assertEqual(values, ["θ", "ð"])

    def test_editorial_beta_sign_is_not_silently_flattened(self) -> None:
        result = decode_text("heƀen", self.profile)
        segment = result["tokens"][0]["segments"][2]
        self.assertEqual(segment["grapheme"], "ƀ")
        self.assertEqual([item["value"] for item in segment["candidates"]], ["β", "v", "b"])

    def test_unicode_casefold_is_reported(self) -> None:
        result = decode_text("Thesa", self.profile)
        self.assertEqual(result["normalized"], "thesa")
        self.assertTrue(result["normalization_changes"])


if __name__ == "__main__":
    unittest.main()
