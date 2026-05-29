import unittest

from crush_service.persona_builder import answer_creator, render_persona_markdown, start_creator


class PersonaBuilderTestCase(unittest.TestCase):
    def test_creator_collects_profile(self) -> None:
        state = start_creator()
        answers = [
            "小满",
            "女",
            "18-25",
            "INFP",
            "推荐",
            "温柔粘人",
            "略主动",
            "偶尔延迟",
            "两者都有",
            "精神浪漫",
            "阴阳怪气",
            "哼",
            "🥺",
            "笨蛋",
            "甜品",
            "暧昧",
        ]
        completed = False
        for answer in answers:
            state, _, completed = answer_creator(state, answer)
        self.assertTrue(completed)
        self.assertEqual(state["profile"]["name"], "小满")
        self.assertEqual(state["profile"]["stage"], "暧昧")

    def test_render_contains_key_fields(self) -> None:
        profile = {
            "name": "小满",
            "gender": "女",
            "age_range": "18-25",
            "user_mbti": "INFP",
            "target_mbti": "ENFJ",
            "love_style": "温柔粘人",
            "proactive_level": "略主动",
            "reply_speed": "偶尔延迟",
            "caring_style": "两者都有",
            "romance_style": "精神浪漫",
            "jealousy_style": "阴阳怪气",
            "catchphrase": "哼",
            "emoji_style": "🥺",
            "addressing": "笨蛋",
            "hobby": "甜品",
            "stage": "暧昧",
        }
        markdown = render_persona_markdown(profile)
        self.assertIn("小满", markdown)
        self.assertIn("ENFJ", markdown)
        self.assertIn("温柔粘人", markdown)

    def test_render_differs_between_styles(self) -> None:
        warm_profile = {
            "name": "阿软",
            "gender": "女",
            "age_range": "18-25",
            "user_mbti": "INFP",
            "target_mbti": "INFJ",
            "love_style": "温柔粘人",
            "proactive_level": "略主动",
            "reply_speed": "偶尔延迟",
            "caring_style": "两者都有",
            "romance_style": "精神浪漫",
            "jealousy_style": "阴阳怪气",
            "catchphrase": "笨蛋",
            "emoji_style": "🥺",
            "addressing": "你",
            "hobby": "甜品",
            "stage": "暧昧",
        }
        cool_profile = {**warm_profile, "name": "阿冷", "love_style": "高冷傲娇", "catchphrase": "哼"}
        warm_markdown = render_persona_markdown(warm_profile)
        cool_markdown = render_persona_markdown(cool_profile)

        self.assertIn("语气软", warm_markdown)
        self.assertIn("嘴硬", cool_markdown)
        self.assertNotEqual(warm_markdown, cool_markdown)


if __name__ == "__main__":
    unittest.main()
