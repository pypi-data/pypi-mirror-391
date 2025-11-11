#!/usr/bin/env python3
"""
agentype - DataAgent 统一使用示例
Author: cuilei
Version: 1.0
"""

import asyncio
import gc
import sys
from pathlib import Path

# 项目根目录
project_root = Path(__file__).resolve().parent.parent

# 导入DataAgent依赖
from agentype.dataagent.config.cache_config import init_cache, get_cache_info
from agentype.dataagent.config.settings import ConfigManager
from agentype.dataagent.agent.data_processor_agent import DataProcessorReactAgent
from agentype.dataagent.utils.i18n import _


async def example_usage():
    """使用示例"""
    print("🧬 CellType DataAgent 统一配置示例")
    print("=" * 50)

    # 创建ConfigManager（可通过环境变量配置）
    import os
    config = ConfigManager(
        openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.siliconflow.cn/v1"),
        openai_api_key=os.getenv("OPENAI_API_KEY", "sk-your-key-here"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        output_dir=os.getenv("OUTPUT_DIR")  # 可选：自定义输出目录
    )

    # 显示配置信息
    print(f"📂 输出目录: {config.output_dir}")
    print(f"📂 结果目录: {config.results_dir}")

    # 初始化DataAgent缓存系统
    cache_dir = init_cache()
    print(f"📂 DataAgent缓存已初始化: {cache_dir}")

    # 显示缓存信息
    cache_info = get_cache_info()
    print(f"📊 缓存状态: {cache_info['agent']} - 存在: {cache_info['exists']}")

    # 创建DataProcessorReactAgent实例
    agent = DataProcessorReactAgent(
        config=config,
        language="zh",
        enable_streaming=False,
    )

    # 测试数据文件（根据实际情况选择）
    test_files = [
        project_root / "test_data" / "sce.rds",  # RDS文件
        project_root / "test_data" / "data.h5ad",  # H5AD文件
        project_root / "test_data" / "data.h5",   # H5文件
        "/root/code/gitpackage/agentype/utils/data.h5ad",  # 备用路径
        "/root/code/gitpackage/agentype/utils/sce.rds",    # 备用路径
    ]

    # 选择存在的测试文件
    test_data_file = None
    for file_path in test_files:
        if Path(file_path).exists():
            test_data_file = str(file_path)
            break

    if not test_data_file:
        print("⚠️  未找到测试数据文件，使用模拟路径进行演示")
        test_data_file = str(project_root / "test_data" / "example.h5ad")

    print(f"📄 处理数据文件: {test_data_file}")

    try:
        print("\n🚀 初始化 DataProcessorReactAgent...")
        if not await agent.initialize():
            print(_("agent.init_failed"))
            return

        print(_("agent.analysis_start"))
        print("🔄 开始数据处理...")

        # 执行数据处理
        result = await agent.process_data(test_data_file)

        # 输出结果
        print("\n" + "=" * 50)
        print("✅ 数据处理完成!")
        print(f"📊 处理成功: {result.get('success', False)}")
        print(f"📏 总迭代次数: {result.get('total_iterations', 0)}")
        print(f"🔧 工具调用次数: {len([log for log in result.get('analysis_log', []) if log.get('type') == 'tool_call'])}")

        # 显示输出文件路径
        output_paths = result.get('output_file_paths', {})
        if output_paths:
            print("\n📁 处理后的文件:")
            for key, path in output_paths.items():
                if path:
                    print(f"   - {key}: {path}")
        else:
            print("📝 没有生成新的输出文件")

        # 显示处理日志概要
        if result.get('analysis_log'):
            print(f"\n📝 处理日志条目: {len(result['analysis_log'])} 条")

        print(f"\n💾 所有输出文件都保存在: {global_config.paths.outputs_dir}")

    except Exception as e:
        print(f"❌ 数据处理过程中发生错误: {e}")
        import traceback
        print("🔍 详细错误信息:")
        traceback.print_exc()

    finally:
        # 清理资源
        print("\n🧹 清理资源...")
        await agent.cleanup()

        # 给异步清理过程额外时间以完成所有资源释放
        await asyncio.sleep(0.5)

        # 强制垃圾回收，清理所有未引用的对象
        gc.collect()

        # 最后一次延迟确保垃圾回收完全完成
        await asyncio.sleep(0.2)

        print("🎉 示例运行完成！")
        print(f"📄 查看详细日志: {agent.config.log_dir}")
        print(f"📊 查看处理结果: {agent.config.results_dir}")
        print(f"💾 查看缓存文件: {cache_dir}")


def main():
    """主函数"""
    print("=" * 60)
    print(" CellType MCP Server - DataAgent 统一配置示例")
    print("=" * 60)
    print()
    print("💡 提示:")
    print("   - 支持处理 RDS、H5AD、H5、CSV、JSON 等多种数据格式")
    print("   - 所有输出文件都保存在统一的 outputs/ 目录下")
    print("   - API密钥可以通过环境变量 OPENAI_API_KEY 设置")
    print("   - 处理后的数据会保存到 outputs/results/celltypeDataAgent/")
    print("   - 更多配置选项请查看 config/agentype_config.json")
    print()

    try:
        asyncio.run(example_usage())
    except KeyboardInterrupt:
        print("\n⚠️  用户中断执行")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()