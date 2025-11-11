#!/usr/bin/env python3
"""
agentype - - MCP服务器启动器
Author: cuilei
Version: 1.0
"""

import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# 导入各Agent的MCP服务器
try:
    from agentype.mainagent.services.mcp_server import main as main_server
except ImportError:
    main_server = None

try:
    from agentype.subagent.services.mcp_server import main as sub_server
except ImportError:
    sub_server = None

try:
    from agentype.dataagent.services.mcp_server import main as data_server
except ImportError:
    data_server = None

try:
    from agentype.appagent.services.mcp_server import main as app_server
except ImportError:
    app_server = None


def setup_logging(level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def start_all_servers():
    """启动所有可用的MCP服务器"""
    parser = argparse.ArgumentParser(
        description="CellType Agent MCP服务器启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
可用的服务器：
  main    - MainAgent MCP服务器 (主调度器)
  sub     - SubAgent MCP服务器 (基础数据服务)
  data    - DataAgent MCP服务器 (数据处理)
  app     - AppAgent MCP服务器 (应用级注释)
  all     - 启动所有可用服务器 (默认)

示例：
  celltype-server                    # 启动所有服务器
  celltype-server main               # 只启动MainAgent
  celltype-server sub data           # 启动SubAgent和DataAgent
  celltype-server --port 8080 main  # 在指定端口启动MainAgent
        """)

    parser.add_argument(
        "servers",
        nargs="*",
        default=["all"],
        choices=["main", "sub", "data", "app", "all"],
        help="要启动的服务器类型"
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="服务器主机地址 (默认: localhost)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="服务器端口 (默认: 自动分配)"
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别 (默认: INFO)"
    )

    parser.add_argument(
        "--concurrent",
        action="store_true",
        help="并发启动多个服务器"
    )

    args = parser.parse_args()

    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # 确定要启动的服务器
    servers_to_start = []
    if "all" in args.servers:
        available_servers = [
            ("main", main_server, "MainAgent MCP服务器"),
            ("sub", sub_server, "SubAgent MCP服务器"),
            ("data", data_server, "DataAgent MCP服务器"),
            ("app", app_server, "AppAgent MCP服务器"),
        ]
        servers_to_start = [(name, func, desc) for name, func, desc in available_servers if func is not None]
    else:
        server_map = {
            "main": (main_server, "MainAgent MCP服务器"),
            "sub": (sub_server, "SubAgent MCP服务器"),
            "data": (data_server, "DataAgent MCP服务器"),
            "app": (app_server, "AppAgent MCP服务器"),
        }

        for server_name in args.servers:
            func, desc = server_map[server_name]
            if func is not None:
                servers_to_start.append((server_name, func, desc))
            else:
                logger.warning(f"服务器 {server_name} 不可用，跳过")

    if not servers_to_start:
        logger.error("没有可用的服务器启动")
        sys.exit(1)

    # 启动服务器
    logger.info(f"准备启动 {len(servers_to_start)} 个服务器")

    if len(servers_to_start) == 1:
        # 只有一个服务器，直接启动
        name, func, desc = servers_to_start[0]
        logger.info(f"启动 {desc}")
        try:
            func()
        except KeyboardInterrupt:
            logger.info("服务器已停止")
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            sys.exit(1)

    elif args.concurrent:
        # 并发启动多个服务器
        logger.info("并发启动多个服务器...")

        async def run_server(name: str, func, desc: str):
            try:
                logger.info(f"启动 {desc}")
                await asyncio.create_subprocess_exec(
                    sys.executable, "-c", f"from {func.__module__} import main; main()",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            except Exception as e:
                logger.error(f"启动 {desc} 失败: {e}")

        async def run_all():
            tasks = [run_server(name, func, desc) for name, func, desc in servers_to_start]
            await asyncio.gather(*tasks, return_exceptions=True)

        try:
            asyncio.run(run_all())
        except KeyboardInterrupt:
            logger.info("所有服务器已停止")

    else:
        # 顺序启动多个服务器
        logger.warning("顺序启动多个服务器。建议使用 --concurrent 选项并发启动。")
        for i, (name, func, desc) in enumerate(servers_to_start):
            logger.info(f"启动第 {i+1}/{len(servers_to_start)} 个服务器: {desc}")
            try:
                func()
            except KeyboardInterrupt:
                logger.info(f"{desc} 已停止")
                break
            except Exception as e:
                logger.error(f"启动 {desc} 失败: {e}")
                continue


def start_single_server(server_type: str, **kwargs):
    """启动单个服务器的便捷函数"""
    server_map = {
        "main": main_server,
        "sub": sub_server,
        "data": data_server,
        "app": app_server,
    }

    func = server_map.get(server_type)
    if func is None:
        raise ValueError(f"未知的服务器类型: {server_type}")

    # 设置临时参数
    original_argv = sys.argv.copy()
    try:
        sys.argv = ["server"]
        for key, value in kwargs.items():
            if key == "host":
                sys.argv.extend(["--host", str(value)])
            elif key == "port":
                sys.argv.extend(["--port", str(value)])

        func()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    start_all_servers()