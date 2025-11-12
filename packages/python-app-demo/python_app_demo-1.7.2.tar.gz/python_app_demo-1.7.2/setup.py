from pathlib import Path

from setuptools import find_packages, setup

README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="python-app-demo",
    version="1.7.2",
    description="示例 Python 项目，通过 logging 和 MCP 输出问候信息。",
    long_description=README,
    long_description_content_type="text/markdown",
    author="baiyx",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.6.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

