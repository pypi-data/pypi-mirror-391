"""MCP 服务实现，复用 CLI 问候逻辑。"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from .logic import make_greeting

logger = logging.getLogger("python_app.mcp")

# 创建 MCP 实例
mcp = FastMCP("python-app-mcp-server", log_level="INFO")

class GreetingRequest(BaseModel):
    """MCP 问候请求体。"""

    name: str = Field(default="世界", description="需要问候的对象名称")


@mcp.tool(description="生成问候语")
async def generate_greeting(request: GreetingRequest | None = None) -> Dict[str, Any]:
    """生成问候语并返回 JSON-RPC 响应。"""
    request = request or GreetingRequest()
    logger.debug("收到 MCP greet 请求: %s", request)

    message = make_greeting(request.name)
    logger.info("生成问候结果: %s", message)

    response = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "result": {
            "success": True,
            "message": message,
        },
    }
    logger.debug("返回 MCP 响应: %s", response)
    return response


@mcp.tool(description="获取当前时间")
async def get_current_time() -> Dict[str, Any]:
    """返回当前时间信息。"""
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    logger.debug("生成时间信息 current_time=%s timestamp=%s", current_time, now.timestamp())

    response = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "result": {
            "success": True,
            "current_time": current_time,
            "timestamp": int(now.timestamp()),
        },
    }
    logger.info("返回当前时间响应")
    return response


def run_mcp_server() -> None:
    """启动 MCP 服务。"""
    logger.info("启动 MCP 服务，transport=stdio")
    mcp.run(transport="stdio")


__all__ = ["run_mcp_server", "mcp"]


if __name__ == "__main__":
    run_mcp_server()

