#!/usr/bin/env python3
"""
agentype - MCP Server 项目管理工具
Author: cuilei
Version: 1.0
"""

import sys
import os
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent

# 导入项目配置
# 注意：GlobalConfig 已废弃，manage.py 将使用默认路径
CONFIG_AVAILABLE = False

# 颜色输出支持
try:
    from colorama import init, Fore, Style
    init()
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

if COLORS_AVAILABLE:
    class Colors:
        GREEN = Fore.GREEN
        YELLOW = Fore.YELLOW
        RED = Fore.RED
        BLUE = Fore.BLUE
        CYAN = Fore.CYAN
        MAGENTA = Fore.MAGENTA
        RESET = Style.RESET_ALL
        BRIGHT = Style.BRIGHT
else:
    class Colors:
        GREEN = ""
        YELLOW = ""
        RED = ""
        BLUE = ""
        CYAN = ""
        MAGENTA = ""
        RESET = ""
        BRIGHT = ""


class ProjectManager:
    """项目管理器"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.agents = ["agentype.mainagent", "agentype.subagent", "agentype.dataagent", "agentype.appagent"]

    def print_colored(self, message: str, color: str = "", end: str = "\n"):
        """带颜色的输出"""
        print(f"{color}{message}{Colors.RESET}", end=end)

    def print_header(self, title: str):
        """打印标题"""
        self.print_colored("=" * 70, Colors.CYAN)
        self.print_colored(f"  🧬 {title}", Colors.CYAN + Colors.BRIGHT)
        self.print_colored("=" * 70, Colors.CYAN)
        print()

    def print_section(self, title: str):
        """打印章节"""
        self.print_colored(f"\n📋 {title}", Colors.BLUE + Colors.BRIGHT)
        self.print_colored("-" * 50, Colors.BLUE)

    def check_project_status(self) -> Dict[str, bool]:
        """检查项目状态"""
        self.print_header("项目状态检查")

        status = {}

        # 检查项目根目录
        self.print_section("项目结构检查")
        status['project_root'] = self.project_root.exists()
        self.print_colored(f"✅ 项目根目录: {self.project_root}", Colors.GREEN if status['project_root'] else Colors.RED)

        # 检查配置目录
        config_dir = self.project_root / "config"
        status['config_dir'] = config_dir.exists()
        self.print_colored(f"{'✅' if status['config_dir'] else '❌'} 配置目录: {config_dir}",
                          Colors.GREEN if status['config_dir'] else Colors.RED)

        # 检查输出目录
        outputs_dir = self.project_root / "outputs"
        status['outputs_dir'] = outputs_dir.exists()
        self.print_colored(f"{'✅' if status['outputs_dir'] else '❌'} 输出目录: {outputs_dir}",
                          Colors.GREEN if status['outputs_dir'] else Colors.RED)

        # 检查Agent目录
        self.print_section("Agent检查")
        for agent in self.agents:
            agent_dir = self.project_root / agent
            status[f'agent_{agent}'] = agent_dir.exists()
            self.print_colored(f"{'✅' if status[f'agent_{agent}'] else '❌'} {agent}: {agent_dir}",
                              Colors.GREEN if status[f'agent_{agent}'] else Colors.RED)

        # 检查配置文件
        self.print_section("配置文件检查")
        config_files = [
            "config/__init__.py",
            "config/global_config.py",
            "config/paths_config.py",
            "config/unified_logger.py",
            "config/agentype_config.json"
        ]

        for config_file in config_files:
            file_path = self.project_root / config_file
            status[f'config_{config_file}'] = file_path.exists()
            self.print_colored(f"{'✅' if status[f'config_{config_file}'] else '❌'} {config_file}",
                              Colors.GREEN if status[f'config_{config_file}'] else Colors.RED)

        # 检查统一配置系统（已废弃）
        self.print_section("统一配置系统检查 (已废弃)")
        status['unified_config'] = False  # GlobalConfig 已废弃
        self.print_colored(f"⚠️  GlobalConfig 已在 v2.0 中废弃", Colors.YELLOW)
        self.print_colored(f"   请使用新的 ConfigManager 系统", Colors.CYAN)
        self.print_colored(f"   详情: 配置传递流程详解.md", Colors.CYAN)
        status['config_load'] = False

        # 旧代码已禁用（GlobalConfig 已废弃）
        # if CONFIG_AVAILABLE:
        #     try:
        #         config = get_global_config()
        #         status['config_load'] = True
        #         ...
        #     except Exception as e:
        #         status['config_load'] = False

        return status

    def check_dependencies(self):
        """检查依赖"""
        self.print_header("依赖检查")

        # Python依赖
        self.print_section("Python依赖")
        python_deps = [
            "colorama",
            "pathlib",
            "json",
            "dataclasses",
            "typing"
        ]

        for dep in python_deps:
            try:
                __import__(dep)
                self.print_colored(f"✅ {dep}", Colors.GREEN)
            except ImportError:
                self.print_colored(f"❌ {dep} - 建议安装: pip install {dep}", Colors.RED)

        # R环境检查 (AppAgent需要)
        self.print_section("R环境检查 (AppAgent需要)")
        try:
            result = subprocess.run(["R", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.print_colored("✅ R环境可用", Colors.GREEN)
                self.print_colored(f"   版本信息: {result.stdout.split()[2] if len(result.stdout.split()) > 2 else 'Unknown'}", Colors.CYAN)
            else:
                self.print_colored("❌ R环境不可用", Colors.RED)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.print_colored("❌ R环境不可用或未安装", Colors.RED)

        # 环境变量检查
        self.print_section("环境变量检查")
        env_vars = [
            "OPENAI_API_KEY",
            "OPENAI_API_BASE",
            "OPENAI_MODEL"
        ]

        for var in env_vars:
            value = os.environ.get(var)
            if value:
                display_value = f"{value[:10]}..." if len(value) > 10 else value
                self.print_colored(f"✅ {var}: {display_value}", Colors.GREEN)
            else:
                self.print_colored(f"⚠️  {var}: 未设置", Colors.YELLOW)

    def clean_outputs(self, confirm: bool = False):
        """清理输出目录"""
        self.print_header("清理输出目录")

        outputs_dir = self.project_root / "outputs"

        if not outputs_dir.exists():
            self.print_colored("📂 outputs目录不存在，无需清理", Colors.YELLOW)
            return

        # 统计文件
        total_files = 0
        total_size = 0

        for file_path in outputs_dir.rglob("*"):
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size

        size_mb = total_size / (1024 * 1024)

        self.print_colored(f"📊 发现 {total_files} 个文件，总大小 {size_mb:.2f} MB", Colors.CYAN)

        if total_files == 0:
            self.print_colored("✅ 目录已经是空的", Colors.GREEN)
            return

        if not confirm:
            response = input(f"\n⚠️  确定要清理所有输出文件吗? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                self.print_colored("❌ 取消清理", Colors.YELLOW)
                return

        try:
            # 清理所有子目录
            subdirs = ['cache', 'logs', 'results', 'downloads']
            for subdir in subdirs:
                subdir_path = outputs_dir / subdir
                if subdir_path.exists():
                    shutil.rmtree(subdir_path)
                    subdir_path.mkdir(exist_ok=True)
                    self.print_colored(f"🗑️  已清理: {subdir}/", Colors.GREEN)

            self.print_colored("✅ 清理完成!", Colors.GREEN)

        except Exception as e:
            self.print_colored(f"❌ 清理失败: {e}", Colors.RED)

    def _show_env_conflicts(self, config):
        """显示环境变量冲突信息"""
        conflicts = []

        # 检查API Base
        env_api_base = os.environ.get("OPENAI_API_BASE")
        if env_api_base and env_api_base != config.llm.api_base:
            conflicts.append({
                'field': 'API Base',
                'env_value': env_api_base,
                'config_value': config.llm.api_base or 'null'
            })

        # 检查API Key
        env_api_key = os.environ.get("OPENAI_API_KEY")
        if env_api_key and env_api_key != config.llm.api_key:
            # 对于API Key，只显示前10位和后4位
            display_env_key = f"{env_api_key[:10]}...{env_api_key[-4:]}" if len(env_api_key) > 14 else env_api_key
            display_config_key = f"{config.llm.api_key[:10]}...{config.llm.api_key[-4:]}" if config.llm.api_key and len(config.llm.api_key) > 14 else (config.llm.api_key or 'null')
            conflicts.append({
                'field': 'API Key',
                'env_value': display_env_key,
                'config_value': display_config_key
            })

        # 检查Model
        env_model = os.environ.get("OPENAI_MODEL")
        if env_model and env_model != config.llm.model:
            conflicts.append({
                'field': 'Model',
                'env_value': env_model,
                'config_value': config.llm.model or 'null'
            })

        # 显示冲突信息
        if conflicts:
            self.print_section("⚠️  环境变量冲突检查")
            self.print_colored("优先使用配置文件的值，如需修改请直接编辑配置文件。", Colors.YELLOW)
            for conflict in conflicts:
                self.print_colored(f"🔸 {conflict['field']}:", Colors.RED)
                self.print_colored(f"   环境变量: {conflict['env_value']}", Colors.GREEN)
                self.print_colored(f"   配置文件: {conflict['config_value']} ← 实际使用", Colors.YELLOW)

    def show_config(self):
        """显示当前配置（已废弃）"""
        self.print_header("当前配置 (功能已废弃)")

        self.print_colored("⚠️  show_config 功能已废弃", Colors.YELLOW)
        self.print_colored("", Colors.RESET)
        self.print_colored("GlobalConfig 配置系统已在 v2.0 中移除。", Colors.CYAN)
        self.print_colored("", Colors.RESET)
        self.print_colored("新的配置方式：", Colors.GREEN)
        self.print_colored("  1. 使用 ConfigManager 直接创建配置：", Colors.CYAN)
        self.print_colored("     from agentype.config import ConfigManager", Colors.WHITE)
        self.print_colored("     config = ConfigManager(", Colors.WHITE)
        self.print_colored("         api_base='https://api.example.com',", Colors.WHITE)
        self.print_colored("         api_key='your-key',", Colors.WHITE)
        self.print_colored("         model='gpt-4o',", Colors.WHITE)
        self.print_colored("         output_dir='./outputs'", Colors.WHITE)
        self.print_colored("     )", Colors.WHITE)
        self.print_colored("", Colors.RESET)
        self.print_colored("  2. 或从环境变量加载：", Colors.CYAN)
        self.print_colored("     config = ConfigManager.from_env()", Colors.WHITE)
        self.print_colored("", Colors.RESET)
        self.print_colored("详情请参阅: 配置传递流程详解.md", Colors.GREEN)
        return

        # 旧代码已禁用（GlobalConfig 已废弃）
        # if not CONFIG_AVAILABLE:
        #     self.print_colored("❌ 统一配置系统不可用", Colors.RED)
        #     return
        # try:
        #     config = get_global_config()
        #     self.print_section("路径配置")
        #     self.print_colored(f"📂 项目根目录: {config.paths.project_root}", Colors.CYAN)
        #     self.print_colored(f"🌐 API Base: {config.llm.api_base or '未设置(使用默认)'}", Colors.CYAN)
        #     self.print_colored(f"🔑 API Key: {'已设置' if config.llm.api_key else '未设置'}", Colors.CYAN)
        #     self.print_colored(f"📊 最大令牌: {config.llm.max_tokens}", Colors.CYAN)
        #     self.print_colored(f"🌡️  温度: {config.llm.temperature}", Colors.CYAN)
        #
        #     # 检查环境变量冲突
        #     self._show_env_conflicts(config)
        #
        #     self.print_section("项目设置")
        #     self.print_colored(f"🌍 语言: {config.project.language}", Colors.CYAN)
        #     self.print_colored(f"📺 流式输出: {config.project.enable_streaming}", Colors.CYAN)
        #     self.print_colored(f"📝 日志记录: {config.project.enable_logging}", Colors.CYAN)
        #     self.print_colored(f"🔄 最大并行任务: {config.project.max_parallel_tasks}", Colors.CYAN)
        #     self.print_colored(f"🗓️  缓存过期天数: {config.project.cache_expiry_days}", Colors.CYAN)
        #     self.print_colored(f"🧹 自动清理: {config.project.auto_cleanup}", Colors.CYAN)
        #
        #     self.print_section("Agent配置")
        #     for agent_name, agent_config in config._agents_config.items():
        #         status_color = Colors.GREEN if agent_config.enabled else Colors.YELLOW
        #         self.print_colored(f"{'✅' if agent_config.enabled else '⚠️ '} {agent_name}: "
        #                          f"启用={agent_config.enabled}, "
        #                          f"重试={agent_config.max_retries}次, 日志={agent_config.log_level}", status_color)
        #
        # except Exception as e:
        #     self.print_colored(f"❌ 读取配置失败: {e}", Colors.RED)

    def run_examples(self):
        """运行示例"""
        self.print_header("运行示例")

        examples_dir = self.project_root / "examples"
        if not examples_dir.exists():
            self.print_colored("❌ examples目录不存在", Colors.RED)
            return

        # 检查运行脚本
        run_script = examples_dir / "run_all_examples.py"
        if run_script.exists():
            self.print_colored(f"🚀 启动统一示例运行器: {run_script}", Colors.GREEN)
            try:
                subprocess.run([sys.executable, str(run_script)], cwd=str(self.project_root))
            except KeyboardInterrupt:
                self.print_colored("\n⚠️  用户中断执行", Colors.YELLOW)
            except Exception as e:
                self.print_colored(f"❌ 运行失败: {e}", Colors.RED)
        else:
            self.print_colored("❌ 统一示例运行器不存在", Colors.RED)

    def show_disk_usage(self):
        """显示磁盘使用情况"""
        self.print_header("磁盘使用情况")

        outputs_dir = self.project_root / "outputs"
        if not outputs_dir.exists():
            self.print_colored("📂 outputs目录不存在", Colors.YELLOW)
            return

        self.print_section("目录大小统计")

        subdirs = ['cache', 'logs', 'results', 'downloads']
        total_size = 0

        for subdir in subdirs:
            subdir_path = outputs_dir / subdir
            if subdir_path.exists():
                size = sum(f.stat().st_size for f in subdir_path.rglob('*') if f.is_file())
                size_mb = size / (1024 * 1024)
                total_size += size

                file_count = sum(1 for f in subdir_path.rglob('*') if f.is_file())
                self.print_colored(f"📁 {subdir}/: {size_mb:.2f} MB ({file_count} 文件)", Colors.CYAN)
            else:
                self.print_colored(f"📁 {subdir}/: 不存在", Colors.YELLOW)

        total_size_mb = total_size / (1024 * 1024)
        self.print_colored(f"\n📊 总计: {total_size_mb:.2f} MB", Colors.GREEN + Colors.BRIGHT)

    def backup_config(self):
        """备份配置"""
        self.print_header("备份配置")

        config_dir = self.project_root / "config"
        if not config_dir.exists():
            self.print_colored("❌ 配置目录不存在", Colors.RED)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / f"config_backup_{timestamp}"

        try:
            shutil.copytree(config_dir, backup_dir)
            self.print_colored(f"✅ 配置已备份到: {backup_dir}", Colors.GREEN)
        except Exception as e:
            self.print_colored(f"❌ 备份失败: {e}", Colors.RED)

    def show_help(self):
        """显示帮助"""
        self.print_header("CellType MCP Server 项目管理工具")

        help_text = """
🔧 可用命令:

  status      - 检查项目状态和配置
  deps        - 检查依赖和环境
  config      - 显示当前配置
  clean       - 清理输出目录
  examples    - 运行示例
  disk        - 显示磁盘使用情况
  backup      - 备份配置文件
  help        - 显示此帮助信息

🚀 快速开始:
  python manage.py status     # 检查项目状态
  python manage.py examples   # 运行示例

💡 环境变量设置:
  export OPENAI_API_KEY="your-api-key"
  export OPENAI_API_BASE="https://api.openai.com/v1"
  export OPENAI_MODEL="gpt-4"

📖 更多信息请查看 examples/README.md
        """

        self.print_colored(help_text, Colors.CYAN)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CellType MCP Server 项目管理工具")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["status", "deps", "config", "clean", "examples", "disk", "backup", "help"],
                       help="要执行的命令")
    parser.add_argument("--force", action="store_true", help="强制执行，不询问确认")

    args = parser.parse_args()

    manager = ProjectManager()

    try:
        if args.command == "status":
            manager.check_project_status()
        elif args.command == "deps":
            manager.check_dependencies()
        elif args.command == "config":
            manager.show_config()
        elif args.command == "clean":
            manager.clean_outputs(confirm=args.force)
        elif args.command == "examples":
            manager.run_examples()
        elif args.command == "disk":
            manager.show_disk_usage()
        elif args.command == "backup":
            manager.backup_config()
        elif args.command == "help":
            manager.show_help()
        else:
            manager.show_help()

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  操作被用户中断{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ 执行失败: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
