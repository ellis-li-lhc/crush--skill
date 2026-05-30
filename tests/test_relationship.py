import unittest

from crush_service.relationship import apply_relationship_progress, build_stage_guidance, build_status_text


class RelationshipTestCase(unittest.TestCase):
    def test_positive_message_increases_favorability(self) -> None:
        result = apply_relationship_progress("陌生", 0, "早安，我有点想你了")
        self.assertGreater(result.favorability, 0)
        self.assertEqual(result.stage_before, "陌生")

    def test_stage_progresses_when_threshold_crossed(self) -> None:
        result = apply_relationship_progress("陌生", 14, "喜欢你，晚安")
        self.assertTrue(result.stage_changed)
        self.assertEqual(result.stage_after, "认识")
        self.assertIsNotNone(result.stage_event)
        self.assertIn("认识", result.stage_event.note)

    def test_stage_guidance_matches_current_stage(self) -> None:
        self.assertIn("轻微试探", build_stage_guidance("暧昧"))

    def test_status_text_contains_core_fields(self) -> None:
        text = build_status_text("暧昧", 42, 9)
        self.assertIn("暧昧", text)
        self.assertIn("42", text)
        self.assertIn("9", text)


if __name__ == "__main__":
    unittest.main()
