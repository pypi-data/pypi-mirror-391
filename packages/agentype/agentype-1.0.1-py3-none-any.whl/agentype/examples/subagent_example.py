#!/usr/bin/env python3
"""
agentype - SubAgent 统一使用示例
Author: cuilei
Version: 1.0
"""

import asyncio
import gc
import sys
from pathlib import Path

# 项目根目录
project_root = Path(__file__).resolve().parent.parent

# 导入SubAgent依赖
from agentype.subagent.config.cache_config import init_cache, get_cache_info
from agentype.subagent.config.settings import ConfigManager
from agentype.subagent.agent.celltype_react_agent import CellTypeReactAgent
from agentype.subagent.utils.file_utils import load_gene_list_from_file
from agentype.subagent.utils.i18n import _


async def example_usage():
    """使用示例"""
    print("🧬 CellType SubAgent 统一配置示例")
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

    # 初始化SubAgent缓存系统
    cache_dir = init_cache()
    print(f"📂 SubAgent缓存已初始化: {cache_dir}")

    # 显示缓存信息
    cache_info = get_cache_info()
    print(f"📊 缓存状态: {cache_info['agent']} - 存在: {cache_info['exists']}")

    # 创建CellTypeReactAgent实例
    agent = CellTypeReactAgent(
        config=config,
        language="zh",
        enable_streaming=False,
    )

    # 示例基因列表文件
    genes_file = project_root / "test_data" / "genes.txt"

    # 如果测试文件不存在，使用mock路径或创建示例基因列表
    if not genes_file.exists():
        genes_file = "/root/code/gitpackage/agentype/utils/genes.txt"
        if not Path(genes_file).exists():
            # 创建示例基因列表
            example_genes = ["CD3D", "CD4", "CD8A", "CD19", "CD14", "FCGR3A"]
            print(f"📝 使用示例基因列表: {example_genes}")
            gene_list = example_genes
        else:
            print(f"📄 加载基因文件: {genes_file}")
            gene_list = load_gene_list_from_file(str(genes_file), max_genes=100)
    else:
        print(f"📄 加载基因文件: {genes_file}")
        gene_list = load_gene_list_from_file(str(genes_file), max_genes=100)

    try:
        print("\n🚀 初始化 CellTypeReactAgent...")
        if not await agent.initialize():
            print(_("agent.init_failed"))
            return

        print(_("agent.analysis_start"))
        print(f"🧬 分析基因列表 ({len(gene_list)} 个基因)")
        print(f"🧬 目标组织: 骨髓")

        # 执行细胞类型分析
        result = await agent.analyze_celltype(gene_list, tissue_type="骨髓")

        # 输出结果
        print("\n" + "=" * 50)
        print("✅ 分析完成!")
        print(f"🧬 推断的细胞类型: {result.get('final_celltype', '未确定')}")
        print(f"📏 总迭代次数: {result.get('total_iterations', 0)}")
        print(f"🔧 工具调用次数: {len([log for log in result.get('analysis_log', []) if log.get('type') == 'tool_call'])}")
        print(f"📊 分析成功: {result.get('success', False)}")

        # 显示分析日志概要
        if result.get('analysis_log'):
            print(f"\n📝 分析日志条目: {len(result['analysis_log'])} 条")

        print(f"\n💾 所有输出文件都保存在: {agent.config.output_dir}")

    except Exception as e:
        print(f"❌ 分析过程中发生错误: {e}")

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
        print(f"💾 查看缓存文件: {cache_dir}")


def main():
    """主函数"""
    print("=" * 60)
    print(" CellType MCP Server - SubAgent 统一配置示例")
    print("=" * 60)
    print()
    print("💡 提示:")
    print("   - 所有缓存和日志都保存在统一的 outputs/ 目录下")
    print("   - API密钥可以通过环境变量 OPENAI_API_KEY 设置")
    print("   - 数据库缓存会自动下载并保存到 outputs/downloads/")
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