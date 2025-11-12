"""MCP 服务实现，提供问候、时间与 Teable 列表等工具。"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from .logic import make_greeting
from .teable_api_client import TeableClient

logger = logging.getLogger("python_app.mcp")

# 创建 MCP 实例
mcp = FastMCP("python-app-mcp-server", log_level="INFO")

# 环境变量键名
TEABLE_BASE_URL_ENV = "TEABLE_BASE_URL"
TEABLE_TOKEN_ENV = "TEABLE_API_TOKEN"
TEABLE_BASE_ID_ENV = "TEABLE_BASE_ID"


class GreetingRequest(BaseModel):
    """MCP 问候请求体。"""

    name: str = Field(default="世界", description="需要问候的对象名称")


class TeableConfig(BaseModel):
    """Teable 连接配置，可显式传入或回退到环境变量。"""

    base_url: str | None = Field(
        default=None,
        description="Teable API 基础地址，如 https://app.teable.cn",
    )
    token: str | None = Field(
        default=None,
        description="Teable 访问令牌，格式为 Bearer token",
    )
    base_id: str | None = Field(
        default=None,
        description="Teable Base ID，用于限定工作区",
    )


def _resolve_teable_config(config: TeableConfig | None) -> TeableConfig:
    """从入参或环境变量解析 Teable 配置。"""

    base_url = (config.base_url if config else None) or os.getenv(TEABLE_BASE_URL_ENV)
    token = (config.token if config else None) or os.getenv(TEABLE_TOKEN_ENV)
    base_id = (config.base_id if config else None) or os.getenv(TEABLE_BASE_ID_ENV)

    missing: List[str] = []
    if not base_url:
        missing.append("base_url")
    if not token:
        missing.append("token")
    if not base_id:
        missing.append("base_id")

    if missing:
        raise ValueError(
            "Teable 配置缺失: "
            + ", ".join(missing)
            + "。可通过 MCP 请求体或环境变量 "
            f"{TEABLE_BASE_URL_ENV}/{TEABLE_TOKEN_ENV}/{TEABLE_BASE_ID_ENV} 提供。"
        )

    logger.debug("解析 Teable 配置成功，base_url=%s base_id=%s", base_url, base_id)
    return TeableConfig(base_url=base_url, token=token, base_id=base_id)


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


@mcp.tool(description="获取 Teable Base 下的表列表")
async def list_teable_tables(config: TeableConfig | None = None) -> Dict[str, Any]:
    """列出 Teable Base 中的所有表格。"""
    logger.info("收到获取 Teable 表列表请求")
    try:
        resolved = _resolve_teable_config(config)
    except ValueError as exc:
        logger.warning("Teable 配置不完整: %s", exc)
        return {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "result": {
                "success": False,
                "message": str(exc),
                "tables": [],
            },
        }

    def _fetch_tables() -> List[Dict[str, Any]]:
        client = TeableClient(resolved.base_url, resolved.token, resolved.base_id)
        return client.get_tables()

    try:
        tables = await asyncio.to_thread(_fetch_tables)
    except Exception as exc:  # pragma: no cover - 依赖外部服务
        logger.exception("获取 Teable 表列表失败: %s", exc)
        return {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "result": {
                "success": False,
                "message": f"获取表列表失败: {exc}",
                "tables": [],
            },
        }

    logger.info("成功获取 Teable 表列表，数量=%d", len(tables))
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "result": {
            "success": True,
            "count": len(tables),
            "tables": tables,
        },
    }


def run_mcp_server() -> None:
    """启动 MCP 服务。"""
    logger.info("启动 MCP 服务，transport=stdio")
    mcp.run(transport="stdio")


__all__ = ["run_mcp_server", "mcp"]


if __name__ == "__main__":
    run_mcp_server()
"""MCP 服务实现，复用 CLI 问候逻辑。"""
