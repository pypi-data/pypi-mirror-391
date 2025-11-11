"""业务逻辑模块，提供可复用的问候功能。"""

from __future__ import annotations

import logging

logger = logging.getLogger("python_app.logic")


def make_greeting(name: str) -> str:
    """生成问候语并记录必要的调试信息。"""
    logger.debug("开始生成问候语，name=%s", name)
    greeting = f"你好，{name}！"
    logger.info("问候语生成完成: %s", greeting)
    return greeting


__all__ = ["make_greeting"]

