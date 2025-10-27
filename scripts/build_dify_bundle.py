#!/usr/bin/env python3
"""
Dify 工作流打包脚本
将模块化的工作流配置和代码文件合并为单个自包含的 YML 文件

用法:
    python scripts/build_dify_bundle.py

输出:
    dify-workflow/music-metadata-checker-bundle.yml
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any


def load_code_file(file_path: Path) -> str:
    """读取 Python 代码文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_http_config(file_path: Path) -> Dict[str, Any]:
    """读取 HTTP 节点配置文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_code_node(node: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
    """处理代码节点，将外部文件内容内嵌"""
    if node.get("type") == "code" and "config" in node:
        config = node["config"]
        if "code_file" in config:
            code_file_path = base_dir / config["code_file"]
            if code_file_path.exists():
                # 读取代码文件内容
                code_content = load_code_file(code_file_path)
                # 替换 code_file 为 code
                del config["code_file"]
                config["code"] = code_content
                print(f"  ✅ 内嵌代码: {code_file_path.name}")
            else:
                print(f"  ⚠️  代码文件不存在: {code_file_path}")

    return node


def process_http_node(node: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
    """处理 HTTP 节点，将外部配置内嵌"""
    if node.get("type") == "http-request" and "config_file" in node:
        config_file_path = base_dir / node["config_file"]
        if config_file_path.exists():
            # 读取配置文件
            http_config = load_http_config(config_file_path)
            # 替换 config_file 为 config
            del node["config_file"]
            node["config"] = http_config.get("config", {})
            if "outputs" in http_config:
                node["outputs"] = http_config["outputs"]
            if "error_handling" in http_config:
                node["error_handling"] = http_config["error_handling"]
            print(f"  ✅ 内嵌配置: {config_file_path.name}")
        else:
            print(f"  ⚠️  配置文件不存在: {config_file_path}")

    return node


def build_bundle():
    """构建自包含的 YML 文件"""
    print("🚀 开始构建 Dify 工作流打包文件...\n")

    # 路径配置
    project_root = Path(__file__).parent.parent
    workflow_dir = project_root / "dify-workflow"
    source_yml = workflow_dir / "music-metadata-checker.yml"
    output_yml = workflow_dir / "music-metadata-checker-bundle.yml"

    # 读取源 YML
    print(f"📖 读取源文件: {source_yml.relative_to(project_root)}")
    with open(source_yml, "r", encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    # 处理节点
    print(f"\n🔧 处理 {len(workflow.get('nodes', []))} 个节点:")
    processed_nodes = []
    for node in workflow.get("nodes", []):
        node_id = node.get("id", "unknown")
        node_type = node.get("type", "unknown")
        print(f"\n  节点: {node_id} ({node_type})")

        # 处理代码节点
        if node_type == "code":
            node = process_code_node(node, workflow_dir)

        # 处理 HTTP 节点
        elif node_type == "http-request":
            node = process_http_node(node, workflow_dir)

        processed_nodes.append(node)

    # 更新节点列表
    workflow["nodes"] = processed_nodes

    # 添加打包元数据
    if "metadata" not in workflow:
        workflow["metadata"] = {}

    workflow["metadata"]["bundled"] = True
    workflow["metadata"]["bundle_version"] = workflow.get("version", "1.0.0")
    workflow["metadata"]["bundle_note"] = (
        "This is a bundled version with all code and configs embedded. "
        "For development, use the modular version in dify-workflow/nodes/"
    )

    # 写入输出文件
    print(f"\n💾 写入打包文件: {output_yml.relative_to(project_root)}")
    with open(output_yml, "w", encoding="utf-8") as f:
        yaml.dump(
            workflow,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )

    print("\n✅ 打包完成！")
    print(f"\n📦 输出文件: {output_yml}")
    print(f"📏 文件大小: {output_yml.stat().st_size / 1024:.2f} KB")
    print("\n🎯 下一步:")
    print("   1. 在 Dify Cloud 选择「导入 DSL 文件」")
    print(f"   2. 上传: {output_yml.name}")
    print("   3. 配置环境变量")
    print("   4. 运行测试\n")


if __name__ == "__main__":
    build_bundle()
