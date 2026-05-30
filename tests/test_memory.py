import unittest

from crush_service.memory import extract_memory_notes, merge_memory_notes


class MemoryTestCase(unittest.TestCase):
    def test_extracts_preferences_and_schedule(self) -> None:
        notes = extract_memory_notes("我喜欢海边，明天要去面试，有点焦虑")

        self.assertTrue(any("偏好" in note and "海边" in note for note in notes))
        self.assertTrue(any("近期安排" in note and "面试" in note for note in notes))
        self.assertTrue(any("情绪线索" in note and "焦虑" in note for note in notes))

    def test_merge_memory_notes_deduplicates_and_limits(self) -> None:
        notes = merge_memory_notes(["偏好：用户喜欢海边"], ["偏好：用户喜欢海边", "称呼：用户希望被称呼为阿离"], limit=2)

        self.assertEqual(notes, ["偏好：用户喜欢海边", "称呼：用户希望被称呼为阿离"])


if __name__ == "__main__":
    unittest.main()
