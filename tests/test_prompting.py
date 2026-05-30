import unittest

from crush_service.persona import PersonaProfile
from crush_service.prompting import ConversationContext, build_messages, build_system_prompt


class PromptingTestCase(unittest.TestCase):
    def test_prompt_includes_memory_and_stage(self) -> None:
        persona = PersonaProfile(
            name="小樱",
            stage="暧昧",
            content="你是一个温柔的人。",
            source_path=None,
        )
        context = ConversationContext(
            user_id="u-1",
            stage="暧昧",
            recent_messages=[{"role": "user", "content": "今天好累"}],
            memory_notes=["用户最近提到：喜欢海边"],
        )
        prompt = build_system_prompt(persona, context)
        self.assertIn("当前关系阶段：暧昧", prompt)
        self.assertIn("喜欢海边", prompt)
        self.assertIn("当前阶段回应重点", prompt)

    def test_build_messages_appends_user_message(self) -> None:
        persona = PersonaProfile(
            name="小樱",
            stage="陌生",
            content="你是一个高冷的人。",
            source_path=None,
        )
        context = ConversationContext(user_id="u-1", stage="陌生")
        messages = build_messages(persona, context, "在干嘛")
        self.assertEqual(messages[-1]["role"], "user")
        self.assertEqual(messages[-1]["content"], "在干嘛")


if __name__ == "__main__":
    unittest.main()
