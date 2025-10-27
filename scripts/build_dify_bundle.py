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


def inline_models_import(code: str, models_file: Path) -> str:
    """
    将 'from models import ...' 替换为 models.py 的实际内容

    Args:
        code: 原始代码
        models_file: models.py 文件路径

    Returns:
        处理后的代码，models.py 内容已内联
    """
    import re

    # 检查是否有 from models import
    if "from models import" not in code:
        return code

    # 读取 models.py 内容
    if not models_file.exists():
        print("    ⚠️  警告: models.py 不存在，无法内联")
        return code

    models_content = load_code_file(models_file)

    # 提取 models.py 中的导入语句（需要保留）
    models_imports = []
    for line in models_content.split("\n"):
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            if "models" not in line:  # 排除自引用
                models_imports.append(line)

    # 提取 models.py 中的实际代码（去除文档字符串和导入）
    lines = models_content.split("\n")
    code_lines = []
    in_docstring = False
    _skip_next = False

    for i, line in enumerate(lines):
        # 跳过文件开头的文档字符串
        if i < 10 and '"""' in line:
            if in_docstring:
                in_docstring = False
                continue
            else:
                in_docstring = True
                continue
        if in_docstring:
            continue

        # 跳过导入语句
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            continue

        # 保留其他代码
        if line.strip():  # 非空行
            code_lines.append(line)

    models_code = "\n".join(code_lines)

    # 在原代码中找到 from models import 的位置
    import_pattern = r"from models import [^\n]+"
    match = re.search(import_pattern, code)

    if match:
        # 构建替换内容
        replacement = f"""# ===== Inlined from models.py =====
{chr(10).join(models_imports)}

{models_code}
# ===== End of models.py =====
"""
        # 替换导入语句
        code = re.sub(import_pattern, replacement, code)
        print("    ✅ 已内联 models.py")

    return code


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

                # 处理 models.py 导入
                models_file = base_dir / "nodes" / "code-nodes" / "models.py"
                code_content = inline_models_import(code_content, models_file)

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
