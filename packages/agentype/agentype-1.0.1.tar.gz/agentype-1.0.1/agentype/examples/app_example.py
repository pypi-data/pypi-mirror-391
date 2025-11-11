#!/usr/bin/env python3
"""
agentype - AppAgent 统一使用示例
Author: cuilei
Version: 1.0
"""

import asyncio
import gc
import sys
from pathlib import Path

# 项目根目录
project_root = Path(__file__).resolve().parent.parent

# 导入AppAgent依赖
from agentype.appagent.config.cache_config import init_cache, get_cache_info
from agentype.appagent.config.settings import ConfigManager
from agentype.appagent.agent.celltype_annotation_agent import CelltypeAnnotationAgent
from agentype.appagent.config.prompts import build_unified_user_query


async def example_usage():
    """使用示例"""
    print("🧬 CellType AppAgent 统一配置示例")
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

    # 初始化AppAgent缓存系统
    cache_dir = init_cache()
    print(f"📂 AppAgent缓存已初始化: {cache_dir}")

    # 显示缓存信息
    cache_info = get_cache_info()
    unified_config_status = cache_info.get('unified_config', False)
    print(f"📊 缓存状态: celltypeAppAgent - 统一配置: {unified_config_status}")

    # 创建CelltypeAnnotationAgent实例
    agent = CelltypeAnnotationAgent(
        config=config,
        language="zh",
        enable_streaming=False,
    )

    # 准备测试输入文件
    # 实际使用时请替换为真实的文件路径
    test_files = {
        'rds_file': None,  # 可以设置为实际的RDS文件路径
        'h5ad_file': None,  # 可以设置为实际的H5AD文件路径
        'h5_file': None,    # 可以设置为实际的H5文件路径
        'marker_genes_json': None,  # 可以设置为实际的标记基因JSON文件路径
    }

    # 检查是否存在测试文件
    test_paths = [
        '/root/code/gitpackage/agentype/utils/data.h5ad',
        '/root/code/gitpackage/agentype/utils/sce.rds',
        str(global_config.get_cache_dir('celltypeDataAgent') / 'data_processed.h5'),
        str(global_config.get_cache_dir('celltypeDataAgent') / 'cluster_marker_genes.json'),
    ]

    available_files = []
    for file_path in test_paths:
        if Path(file_path).exists():
            available_files.append(file_path)
            if file_path.endswith('.h5ad'):
                test_files['h5ad_file'] = file_path
            elif file_path.endswith('.rds'):
                test_files['rds_file'] = file_path
            elif file_path.endswith('.h5'):
                test_files['h5_file'] = file_path
            elif file_path.endswith('.json'):
                test_files['marker_genes_json'] = file_path

    print(f"📄 可用的测试文件: {len(available_files)} 个")
    for file_path in available_files:
        print(f"   - {Path(file_path).name}: {file_path}")

    # 如果没有找到测试文件，使用示例路径
    if not any(test_files.values()):
        print("⚠️  未找到测试数据文件，使用示例路径进行演示")
        test_files['h5ad_file'] = str(project_root / "test_data" / "example.h5ad")

    # 设置分析参数
    tissue = '骨髓'  # 目标组织类型
    species = 'Mouse'  # 物种（Human/Mouse）
    cluster_column = 'seurat_clusters'  # 聚类列名，可根据数据集自定义

    # 展示统一查询模板
    print(f"\n🧬 分析参数:")
    print(f"   - 组织类型: {tissue}")
    print(f"   - 物种: {species}")
    print(f"   - 语言: {global_config.project.language}")

    unified_query = build_unified_user_query(
        file_paths=test_files,
        tissue_description=tissue,
        species=species,
        language=global_config.project.language,
        cluster_column=cluster_column,
    )
    print(f"\n📝 统一查询模板预览:")
    print("─" * 50)
    print(unified_query[:300] + "..." if len(unified_query) > 300 else unified_query)
    print("─" * 50)

    try:
        print("\n🚀 初始化 CelltypeAnnotationAgent...")
        if not await agent.initialize():
            print("❌ Agent 初始化失败")
            return

        print("🔬 开始细胞类型注释分析...")
        print("   支持的注释方法: SingleR, scType, CellTypist")

        # 使用统一模板调用注释（React 循环）
        result = await agent.annotate(
            rds_path=test_files['rds_file'],
            h5ad_path=test_files['h5ad_file'],
            h5_path=test_files['h5_file'],
            marker_json_path=test_files['marker_genes_json'],
            tissue_description=tissue,
            species=species,
            cluster_column=cluster_column,
        )

        # 输出结果摘要
        print("\n" + "=" * 50)
        print("✅ 注释分析完成!")
        print(f"📊 执行成功: {result.get('success', False)}")
        print(f"📏 总迭代次数: {result.get('total_iterations', 0)}")
        print(f"🔧 工具调用次数: {len([x for x in result.get('analysis_log', []) if x.get('type')=='tool_call'])}")

        # 解析的输出文件路径（如果 LLM 在 <final_answer> 之后提供了 <file_paths>）
        out_paths = result.get('output_file_paths') or {}
        if out_paths:
            print("\n📁 生成的注释结果文件:")
            for key, path in out_paths.items():
                if path:
                    print(f"   - {key}: {path}")
        else:
            print("📝 没有检测到输出文件路径")

        # 显示分析日志概要
        if result.get('analysis_log'):
            print(f"\n📝 分析日志条目: {len(result['analysis_log'])} 条")

        print(f"\n💾 所有输出文件都保存在: {global_config.paths.outputs_dir}")

    except Exception as e:
        print(f"❌ 注释过程中发生错误: {e}")
        import traceback
        print("🔍 详细错误信息:")
        traceback.print_exc()

    finally:
        # 清理资源
        print("\n🧹 清理资源...")
        await agent.cleanup()
        await asyncio.sleep(0.3)
        gc.collect()
        await asyncio.sleep(0.1)

        print("🎉 示例运行完成！")
        print(f"📄 查看详细日志: {agent.config.log_dir}")
        print(f"📊 查看注释结果: {agent.config.results_dir}")
        print(f"💾 查看缓存文件: {cache_dir}")


def main():
    """主函数"""
    print("=" * 60)
    print(" CellType MCP Server - AppAgent 统一配置示例")
    print("=" * 60)
    print()
    print("💡 提示:")
    print("   - 集成 SingleR、scType 和 CellTypist 三种注释方法")
    print("   - 所有输出文件都保存在统一的 outputs/ 目录下")
    print("   - API密钥可以通过环境变量 OPENAI_API_KEY 设置")
    print("   - 注释结果会保存到 outputs/results/celltypeAppAgent/")
    print("   - 需要安装相关依赖: R环境(SingleR, scType), Python(CellTypist)")
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
