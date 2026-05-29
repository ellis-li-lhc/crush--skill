import unittest

from crush_service.style_library import get_style_preset, resolve_style_key


class StyleLibraryTestCase(unittest.TestCase):
    def test_exact_style_lookup(self) -> None:
        preset = get_style_preset("高冷傲娇")
        self.assertEqual(preset.key, "高冷傲娇")
        self.assertIn("嘴硬", preset.voice)

    def test_fuzzy_style_lookup_falls_back_by_containment(self) -> None:
        key = resolve_style_key("有点高冷傲娇但会黏人")
        self.assertEqual(key, "高冷傲娇")

    def test_unknown_style_falls_back_to_warm_default(self) -> None:
        preset = get_style_preset("神秘系")
        self.assertEqual(preset.key, "温柔粘人")


if __name__ == "__main__":
    unittest.main()
