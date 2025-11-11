#!/usr/bin/env python3
"""
agentype - 运行所有Agent示例的统一入口脚本
Author: cuilei
Version: 1.0
"""

import sys
import os
import subprocess
from pathlib import Path


def print_header():
    """打印欢迎头部"""
    print("=" * 70)
    print("   🧬 CellType MCP Server - 统一配置示例演示")
    print("=" * 70)
    print()


def print_menu():
    """打印菜单选项"""
    print("请选择要运行的Agent示例:")
    print()
    print("  1️⃣  MainAgent    - 主调度器 (统一工作流编排)")
    print("  2️⃣  SubAgent     - 基础数据服务 (基因查询、富集分析)")
    print("  3️⃣  DataAgent    - 数据处理 (格式转换、预处理)")
    print("  4️⃣  AppAgent     - 应用级注释 (SingleR/scType/CellTypist)")
    print()
    print("  0️⃣  退出")
    print()


def cleanup_outputs():
    """清理输出目录"""
    try:
        project_root = Path(__file__).resolve().parent.parent
        outputs_dir = project_root / "outputs"

        if not outputs_dir.exists():
            print("📂 outputs 目录不存在，无需清理")
            return

        print(f"🧹 准备清理输出目录: {outputs_dir}")

        # 统计当前文件
        total_files = sum(1 for _ in outputs_dir.rglob("*") if _.is_file())
        total_size = sum(_.stat().st_size for _ in outputs_dir.rglob("*") if _.is_file())
        size_mb = total_size / (1024 * 1024)

        print(f"📊 当前状态: {total_files} 个文件，总大小 {size_mb:.2f} MB")

        if total_files == 0:
            print("✅ 目录已经是空的")
            return

        confirm = input("\n⚠️  确定要清理所有输出文件吗? (y/N): ").strip().lower()

        if confirm in ['y', 'yes']:
            import shutil

            # 删除所有子目录内容，但保留目录结构
            for subdir in ['cache', 'logs', 'results', 'downloads']:
                subdir_path = outputs_dir / subdir
                if subdir_path.exists():
                    shutil.rmtree(subdir_path)
                    subdir_path.mkdir(exist_ok=True)
                    print(f"🗑️  已清理: {subdir}/")

            print("✅ 清理完成!")
        else:
            print("❌ 取消清理")

    except Exception as e:
        print(f"❌ 清理失败: {e}")


def run_example(example_name: str):
    """运行指定的示例"""
    project_root = Path(__file__).resolve().parent.parent
    examples_dir = project_root / "examples"

    example_files = {
        "main": "main_example.py",
        "sub": "subagent_example.py",
        "data": "data_example.py",
        "app": "app_example.py"
    }

    if example_name not in example_files:
        print(f"❌ 未知的示例类型: {example_name}")
        return False

    example_file = examples_dir / example_files[example_name]

    if not example_file.exists():
        print(f"❌ 示例文件不存在: {example_file}")
        return False

    print(f"🚀 正在运行: {example_files[example_name]}")
    print("=" * 50)

    try:
        # 设置工作目录为项目根目录
        result = subprocess.run(
            [sys.executable, str(example_file)],
            cwd=str(project_root),
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ 示例运行失败，退出码: {e.returncode}")
        return False
    except KeyboardInterrupt:
        print("\n⚠️  用户中断执行")
        return False
    except Exception as e:
        print(f"❌ 运行示例时发生错误: {e}")
        return False


def main():
    """主函数"""
    print_header()

    # 检查环境
    project_root = Path(__file__).resolve().parent.parent
    if not (project_root / "config").exists():
        print("❌ 配置目录不存在，请确保在正确的项目根目录下运行")
        sys.exit(1)

    # 显示环境信息
    print("🌍 运行环境:")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   工作目录: {project_root}")
    print(f"   API密钥: {'已设置' if os.environ.get('OPENAI_API_KEY') else '未设置'}")
    print()

    while True:
        print_menu()
        choice = input("请选择 (0-6): ").strip()

        if choice == "0":
            print("\n👋 再见！")
            break
        elif choice == "1":
            print("\n🎯 选择: MainAgent 示例")
            run_example("main")
        elif choice == "2":
            print("\n🎯 选择: SubAgent 示例")
            run_example("sub")
        elif choice == "3":
            print("\n🎯 选择: DataAgent 示例")
            run_example("data")
        elif choice == "4":
            print("\n🎯 选择: AppAgent 示例")
            run_example("app")
        else:
            print("❌ 无效的选择，请重新输入")

        print("\n" + "=" * 50)
        input("按 Enter 键继续...")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        sys.exit(1)
