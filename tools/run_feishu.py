#!/usr/bin/env python3
"""飞书恋爱对象机器人启动入口。"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from crush_service.app import create_app
from crush_service.config import load_config
from crush_service.logging_utils import configure_logging


def main() -> None:
    config = load_config()
    configure_logging(config.log_level)
    app = create_app(config)
    app.run(host=config.host, port=config.port)


if __name__ == "__main__":
    main()
