#!/usr/bin/env python3
"""
agentype - 项目安装配置
Author: cuilei
Version: 1.0
"""

from setuptools import setup, find_packages
from pathlib import Path
import os

# 读取README文件
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

# 从pyproject.toml中提取版本信息
version = "1.0.1"
try:
    import tomllib
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            version = pyproject_data.get("project", {}).get("version", version)
except ImportError:
    # Python < 3.11 fallback
    pass

# 核心依赖（与pyproject.toml保持一致）
core_requirements = [
    "mcp>=1.0.0",
    "fastmcp>=0.3.0",
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "asyncio-mqtt>=0.16.0",
    "aiofiles>=23.2.1",
    "websockets>=12.0",
    "numpy>=1.24.0,<2.0",
    "pandas>=2.1.0,<2.2.0",
    "scipy>=1.11.0",
    "scanpy>=1.9.0",
    "anndata>=0.10.0",
    "gseapy>=1.1.0",
    "h5py>=3.10.0",
    "tables>=3.9.0",
    "openpyxl>=3.1.0",
    "requests>=2.31.0",
    "httpx>=0.25.0",
    "pyyaml>=6.0",
    "jsonschema>=4.20.0",
    "loguru>=0.7.0",
    "click>=8.1.0",
    "rich>=13.7.0",
    "tqdm>=4.66.0",
    "pathlib2>=2.3.7",
    "filetype>=1.2.0",
    "typing-extensions>=4.8.0",
    "pydantic-settings>=2.1.0",
    "babel>=2.13.0",
    "python-i18n>=0.3.9",
    "psutil>=5.9.0",
    "python-dateutil>=2.8.0",
    "pytz>=2023.3",
]

# 包信息
setup(
    name="agentype",
    version=version,
    author="CellType Agent Team",
    author_email="contact@agentype.com",
    description="统一的细胞类型分析工具包，集成四个专业Agent提供完整的细胞类型注释流程",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agentype/celltype-agent",
    project_urls={
        "Bug Tracker": "https://github.com/agentype/celltype-agent/issues",
        "Documentation": "https://github.com/agentype/celltype-agent/wiki",
        "Source": "https://github.com/agentype/celltype-agent",
        "Changelog": "https://github.com/agentype/celltype-agent/blob/main/CHANGELOG.md",
    },

    # 包配置
    packages=find_packages(
        include=["agentype*"],
        exclude=[
            "tests*",
            "outputs*",
            "logs*",
            ".claude*",
            "*.egg-info*"
        ]
    ),

    # 包数据配置
    package_data={
        "": [
            "*.json",
            "*.yaml",
            "*.yml",
            "*.R",
            "*.r",
            "locales/**/*.json",
            "templates/**/*",
            "data/**/*",
        ],
        "agentype.appagent": [
            "tools/r/*.R",
            "tools/r/*.r",
            "tools/r/sctype/*.R",
            "tools/r/sctype/*.r",
            "tools/r/sctype/*.xlsx",
            "locales/*.json",
        ],
        "agentype.mainagent": [
            "locales/*.json",
        ],
        "agentype.subagent": [
            "locales/*.json",
        ],
        "agentype.dataagent": [
            "locales/*.json",
        ],
        "agentype.config": [
            "*.json",
            "*.yaml",
            "*.yml",
        ],
    },
    include_package_data=True,

    # Python版本要求
    python_requires=">=3.8",

    # 核心依赖
    install_requires=core_requirements,

    # 可选依赖
    extras_require={
        # 细胞类型注释工具
        "annotation": [
            "celltypist>=1.6.0",
            "rpy2>=3.5.0",
            "bioservices>=1.11.0",
            "biopython>=1.81",
        ],
        # 机器学习增强
        "ml": [
            "scikit-learn>=1.3.0",
            "torch>=2.0.0",
            "numba>=0.58.0",
        ],
        # 可视化支持
        "viz": [
            "matplotlib>=3.8.0",
            "seaborn>=0.12.0",
            "plotly>=5.17.0",
        ],
        # 性能优化
        "performance": [
            "dask[complete]>=2023.12.0",
            "joblib>=1.3.0",
            "diskcache>=5.6.0",
        ],
        # 部署相关
        "deploy": [
            "gunicorn>=21.2.0",
            "docker>=6.1.0",
        ],
        # 开发依赖
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "ruff>=0.1.0",
        ],
    },

    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
    ],

    # 关键词
    keywords=[
        "single-cell",
        "RNA-seq",
        "cell-type",
        "annotation",
        "SingleR",
        "scType",
        "CellTypist",
        "bioinformatics",
        "genomics",
        "MCP"
    ],

    # 命令行工具
    entry_points={
        "console_scripts": [
            "celltype-manage=manage:main",
            "celltype-server=agentype.servers:start_all_servers",
        ],
    },

    # 许可证
    license="MIT",

    # 压缩
    zip_safe=False,

    # 元数据
    platforms=["any"],
)
