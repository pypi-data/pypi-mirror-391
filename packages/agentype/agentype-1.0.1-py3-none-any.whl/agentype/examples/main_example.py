#!/usr/bin/env python3
"""
agentype - MainAgent 统一使用示例
Author: cuilei
Version: 1.0
"""

import asyncio
import gc
import sys
from pathlib import Path

# 项目根目录
project_root = Path(__file__).resolve().parent.parent

# 导入MainAgent依赖
from agentype.mainagent.config.cache_config import init_cache
from agentype.mainagent.config.settings import ConfigManager
from agentype.mainagent.agent.main_react_agent import MainReactAgent


async def example_usage():
    """使用示例"""
    print("🧬 CellType MainAgent 统一配置示例")
    print("=" * 50)

    # 创建ConfigManager（可通过环境变量配置）
    import os
    config = ConfigManager(
        openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.siliconflow.cn/v1"),
        openai_api_key=os.getenv("OPENAI_API_KEY", "sk-your-key-here"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        language="zh",
        enable_streaming=False,
        output_dir=os.getenv("OUTPUT_DIR")  # 可选：自定义输出目录
    )

    # 显示配置信息
    print(f"📂 缓存目录: {config.cache_dir}")
    print(f"📂 日志目录: {config.log_dir}")
    print(f"📂 结果目录: {config.results_dir}")

    # 初始化MainAgent缓存系统
    cache = init_cache()
    print(f"📂 MainAgent缓存已初始化: {cache.cache_dir}")

    # 创建MainReactAgent实例
    agent = MainReactAgent(
        config=config,
        language=config.language,
        enable_streaming=config.enable_streaming,
    )

    # 使用示例数据文件（请根据实际情况调整路径）
    test_data_file = project_root / "test_data" / "sce.rds"
    test_tissue = "骨髓"

    # 如果测试文件不存在，使用mock路径
    if not test_data_file.exists():
        test_data_file = "/root/code/gitpackage/agentype/utils/sce.rds"
        print(f"📄 使用测试文件: {test_data_file}")

    try:
        print("\n🚀 初始化 MainReactAgent...")
        if not await agent.initialize():
            print("❌ 初始化失败")
            return

        print(f"🧬 开始分析 - 组织类型: {test_tissue}")
        print(f"📁 数据文件: {test_data_file}")

        # 调用主工作流（传入RDS路径与组织类型）
        result = await agent.process_with_llm_react(
            input_data=str(test_data_file),
            tissue_type=test_tissue
        )

        # 输出摘要
        print("\n" + "=" * 50)
        print("✅ 分析完成!")
        print(f"📊 执行结果: {result.get('success', False)}")
        print(f"🧬 目标组织: {test_tissue}")
        print(f"📏 总迭代次数: {result.get('total_iterations', 0)}")

        # 输出文件路径
        if result.get("output_file_paths"):
            print("\n📁 生成的文件:")
            for key, path in result["output_file_paths"].items():
                if path:
                    print(f"   - {key}: {path}")

        print(f"\n💾 所有输出文件都保存在: {global_config.paths.outputs_dir}")

    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")

    finally:
        # 清理资源
        print("\n🧹 清理资源...")
        await agent.cleanup()
        await asyncio.sleep(0.5)
        gc.collect()
        await asyncio.sleep(0.2)

        print("🎉 示例运行完成！")
        print(f"📄 查看详细日志: {agent.config.log_dir}")
        print(f"📊 查看分析结果: {agent.config.results_dir}")


def main():
    """主函数"""
    print("=" * 60)
    print(" CellType MCP Server - MainAgent 统一配置示例")
    print("=" * 60)
    print()
    print("💡 提示:")
    print("   - 所有输出文件都保存在统一的 outputs/ 目录下")
    print("   - API密钥可以通过环境变量 OPENAI_API_KEY 设置")
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