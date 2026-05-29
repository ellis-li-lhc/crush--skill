import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from crush_service.config import load_config


class ConfigTestCase(unittest.TestCase):
    def test_env_overrides_file_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            config_path.write_text(
                """
                {
                  "feishu": {"app_id": "file-app", "app_secret": "file-secret"},
                  "ai": {"provider": "openai", "api_key": "file-key", "model": "file-model"},
                  "personality": {"path": "./crush-default/personality.md"}
                }
                """,
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {
                    "FEISHU_APP_ID": "env-app",
                    "FEISHU_APP_SECRET": "env-secret",
                    "AI_API_KEY": "env-key",
                    "AI_PROVIDER": "deepseek",
                    "AI_MODEL": "deepseek-chat",
                },
                clear=False,
            ):
                config = load_config(config_path)

        self.assertEqual(config.feishu.app_id, "env-app")
        self.assertEqual(config.ai.provider, "deepseek")
        self.assertEqual(config.ai.model, "deepseek-chat")


if __name__ == "__main__":
    unittest.main()
