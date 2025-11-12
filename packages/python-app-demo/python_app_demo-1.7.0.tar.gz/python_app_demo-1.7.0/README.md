# Python 示例项目

本项目使用 `setuptools` 和 `pyproject.toml` 管理依赖，示范如何构建可执行的命令行工具。

## 快速开始

0. 进入项目目录
   ```bash
   cd python_app
   ```
1. 创建虚拟环境
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. 安装依赖
   ```bash
   pip install -e .[dev]
   ```
3. 运行主程序
   ```bash
   python-app-demo --name 世界
   ```
4. 运行测试
   ```bash
   pytest
   ```

## 项目结构

```
├── pyproject.toml
├── README.md
├── src
│   └── app
│       ├── __init__.py
│       └── main.py
└── tests
    ├── __init__.py
    └── test_main.py
```

## 日志

主程序使用标准库 `logging` 记录调试与信息级别的日志，并在处理用户输入时输出详细信息，方便排查问题。

## MCP 服务

命令行新增 `--mode mcp` 参数，可启动基于 `FastMCP` 的服务，当前暴露以下工具：

- `generate_greeting`：生成问候语，复用 CLI 逻辑。
- `get_current_time`：返回当前时间与时间戳。

示例：

```bash
python -m app.main --mode mcp
```

如需在 MCP 模式下使用 Teable 相关工具，可通过命令行参数传入配置（优先级高于环境变量）：

```bash
python -m app.main --mode mcp \
  --teable-base-url https://app.teable.cn \
  --teable-token "teable_xxx" \
  --teable-base-id bseXXXXXXXXXXXX
```
```
Requires:
- Python >= 3.10
```

