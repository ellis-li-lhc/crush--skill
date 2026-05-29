import unittest

from tools.mbti_lib import get_compatibility, recommend_types


class MbtiTestCase(unittest.TestCase):
    def test_get_compatibility_returns_expected_score(self) -> None:
        result = get_compatibility("INTJ", "ENFP")
        self.assertEqual(result["score"], 95)
        self.assertEqual(result["level"], "best")

    def test_recommend_types_honors_limit(self) -> None:
        results = recommend_types("INFP", limit=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["mbti"], "ENFJ")


if __name__ == "__main__":
    unittest.main()
