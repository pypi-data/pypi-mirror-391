"""应用入口模块，包含命令行执行逻辑。"""

from __future__ import annotations

import argparse
import logging
import os

from .logic import make_greeting

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("python_app")


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="简单的问候程序")
    parser.add_argument(
        "--name",
        default="世界",
        help="需要问候的对象名称",
    )
    parser.add_argument(
        "--mode",
        choices=("cli", "mcp"),
        default="cli",
        help="运行模式，cli 输出问候语，mcp 启动 MCP 服务。",
    )
    parser.add_argument(
        "--teable-base-url",
        default=None,
        help="Teable API 基础地址（仅在 MCP 模式下生效，可覆盖环境变量 TEABLE_BASE_URL）。",
    )
    parser.add_argument(
        "--teable-token",
        default=None,
        help="Teable API 访问令牌（仅在 MCP 模式下生效，可覆盖环境变量 TEABLE_API_TOKEN）。",
    )
    parser.add_argument(
        "--teable-base-id",
        default=None,
        help="Teable Base ID（仅在 MCP 模式下生效，可覆盖环境变量 TEABLE_BASE_ID）。",
    )
    return parser


def greet(name: str) -> str:
    """返回问候语，同时记录日志。"""
    logger.debug("准备生成问候语，参数 name=%s", name)
    greeting = make_greeting(name)
    logger.info("生成问候语: %s", greeting)
    return greeting


def main(raw_args: list[str] | None = None) -> int:
    """入口函数，在命令行环境和 tests 中复用。"""
    logger.debug("应用启动，raw_args=%s", raw_args)
    parser = build_parser()
    args = parser.parse_args(raw_args)
    logger.debug("解析参数完成，args=%s", args)

    if args.mode == "mcp":
        logger.info("进入 MCP 模式，开始启动服务")
        if args.teable_base_url:
            os.environ["TEABLE_BASE_URL"] = args.teable_base_url
            logger.debug("已通过启动参数设置 TEABLE_BASE_URL")
        if args.teable_token:
            os.environ["TEABLE_API_TOKEN"] = args.teable_token
            logger.debug("已通过启动参数设置 TEABLE_API_TOKEN")
        if args.teable_base_id:
            os.environ["TEABLE_BASE_ID"] = args.teable_base_id
            logger.debug("已通过启动参数设置 TEABLE_BASE_ID")

        try:
            from .mcp_service import run_mcp_server
        except ImportError as exc:
            logger.exception("加载 MCP 服务模块失败: %s", exc)
            return 1
        run_mcp_server()
        logger.info("MCP 服务正常退出")
        return 0

    logger.debug("进入 CLI 模式，准备生成问候信息")
    message = greet(args.name)
    logger.debug("即将输出问候语: %s", message)
    print(message)

    logger.info("程序执行完毕，没有出现错误")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

