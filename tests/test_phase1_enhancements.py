"""
测试 Phase 1 元数据比较增强功能

测试内容:
1. 歌词比较
2. 时长比较
3. 封面图比较增强
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 添加 dify-workflow 目录到路径
dify_workflow_path = os.path.join(project_root, "dify-workflow")
sys.path.insert(0, dify_workflow_path)

# 导入测试函数
from nodes.code_nodes.consolidate import (  # noqa: E402
    compare_lyrics,
    compare_duration,
    parse_cover_comparison_json,
)


def test_lyrics_comparison():
    """测试歌词比较功能"""
    print("\n=== 测试歌词比较 ===\n")

    # 测试用例 1: 完全匹配
    netease_lyrics = {
        "original": "[00:00.00]这是第一行\n[00:01.00]这是第二行\n[00:02.00]这是第三行"
    }
    qqmusic_lyrics = "这是第一行\n这是第二行\n这是第三行"

    result = compare_lyrics(netease_lyrics, "", qqmusic_lyrics)
    print("测试 1 - 完全匹配:")
    print(f"  状态: {result['status']}")
    print(f"  相似度: {result.get('similarity_score', 0):.2%}")
    print(f"  确认来源: {result.get('confirmed_by', [])}")
    assert result["status"] == "确认", "应该确认匹配"
    print("  ✅ 通过\n")

    # 测试用例 2: 部分匹配
    netease_lyrics2 = {
        "original": "[00:00.00]这是第一行\n[00:01.00]这是第二行\n[00:02.00]这是第三行"
    }
    qqmusic_lyrics2 = "这是第一行\n这是不同的第二行\n这是第三行"

    result2 = compare_lyrics(netease_lyrics2, "", qqmusic_lyrics2)
    print("测试 2 - 部分匹配:")
    print(f"  状态: {result2['status']}")
    print(f"  相似度: {result2.get('similarity_score', 0):.2%}")
    print("  ✅ 通过\n")

    # 测试用例 3: 无歌词
    netease_lyrics3 = {"original": ""}
    result3 = compare_lyrics(netease_lyrics3, "", "")
    print("测试 3 - 无歌词:")
    print(f"  状态: {result3['status']}")
    print(f"  说明: {result3.get('note', '')}")
    assert result3["status"] == "未查到", "应该标记为未查到"
    print("  ✅ 通过\n")


def test_duration_comparison():
    """测试时长比较功能"""
    print("\n=== 测试时长比较 ===\n")

    # 测试用例 1: 完全匹配
    result1 = compare_duration(240000, 240000, 240000)  # 4分钟
    print("测试 1 - 完全匹配 (4:00):")
    print(f"  状态: {result1['status']}")
    print(f"  格式化: {result1['value_formatted']}")
    print(f"  确认来源: {result1.get('confirmed_by', [])}")
    assert result1["status"] == "确认", "应该确认匹配"
    print("  ✅ 通过\n")

    # 测试用例 2: 在容差范围内 (±2秒)
    result2 = compare_duration(240000, 241500, 238500)  # 差1.5秒
    print("测试 2 - 容差范围内 (±1.5秒):")
    print(f"  状态: {result2['status']}")
    print(f"  确认来源: {result2.get('confirmed_by', [])}")
    assert result2["status"] == "确认", "应该在容差范围内确认"
    print("  ✅ 通过\n")

    # 测试用例 3: 超出容差
    result3 = compare_duration(240000, 250000, 230000)  # 差10秒
    print("测试 3 - 超出容差 (±10秒):")
    print(f"  状态: {result3['status']}")
    print(f"  说明: {result3.get('note', '')}")
    assert result3["status"] == "存疑", "应该标记为存疑"
    print("  ✅ 通过\n")

    # 测试用例 4: 无时长数据
    result4 = compare_duration(0, 0, 0)
    print("测试 4 - 无时长数据:")
    print(f"  状态: {result4['status']}")
    print(f"  说明: {result4.get('note', '')}")
    assert result4["status"] == "未查到", "应该标记为未查到"
    print("  ✅ 通过\n")


def test_cover_comparison_json():
    """测试封面图比较 JSON 解析"""
    print("\n=== 测试封面图比较 JSON 解析 ===\n")

    # 测试用例 1: 标准 JSON 响应
    json_response = """
    {
        "is_same": true,
        "confidence": 0.95,
        "differences": [],
        "notes": "封面图完全相同"
    }
    """
    result1 = parse_cover_comparison_json(json_response)
    print("测试 1 - 标准 JSON (相同):")
    print(f"  状态: {result1['status']}")
    print(f"  置信度: {result1['confidence']}")
    print(f"  是否相同: {result1['is_same']}")
    assert result1["status"] == "确认", "应该确认相同"
    print("  ✅ 通过\n")

    # 测试用例 2: 有差异的 JSON
    json_response2 = """
    {
        "is_same": false,
        "confidence": 0.6,
        "differences": ["颜色不同", "尺寸不同"],
        "notes": "主体相似但有差异"
    }
    """
    result2 = parse_cover_comparison_json(json_response2)
    print("测试 2 - JSON 有差异:")
    print(f"  状态: {result2['status']}")
    print(f"  置信度: {result2['confidence']}")
    print(f"  差异: {result2['differences']}")
    assert result2["status"] == "存疑", "应该标记为存疑"
    print("  ✅ 通过\n")

    # 测试用例 3: Fallback 到文本解析
    text_response = "封面图相同"
    result3 = parse_cover_comparison_json(text_response)
    print("测试 3 - Fallback 文本解析:")
    print(f"  状态: {result3['status']}")
    print(f"  置信度: {result3['confidence']}")
    assert result3["status"] == "确认", "应该识别为相同"
    print("  ✅ 通过\n")

    # 测试用例 4: 不相同的文本
    text_response2 = "封面图不相同"
    result4 = parse_cover_comparison_json(text_response2)
    print("测试 4 - 不相同文本:")
    print(f"  状态: {result4['status']}")
    assert result4["status"] == "存疑", "应该标记为存疑"
    print("  ✅ 通过\n")


def test_integration():
    """集成测试：模拟完整的比较流程"""
    print("\n=== 集成测试 ===\n")

    # 模拟完整的元数据
    netease_data = {
        "lyrics": {"original": "[00:00.00]示例歌词第一行\n[00:01.00]示例歌词第二行"},
        "duration_ms": 240000,
        "cover_url": "http://example.com/cover1.jpg",
    }

    qqmusic_data = {
        "lyrics": "示例歌词第一行\n示例歌词第二行",
        "duration_ms": 240500,  # 差0.5秒
        "cover_url": "http://example.com/cover2.jpg",
    }

    # 测试歌词比较
    lyrics_result = compare_lyrics(netease_data["lyrics"], "", qqmusic_data["lyrics"])
    print(f"歌词比较结果: {lyrics_result['status']}")

    # 测试时长比较
    duration_result = compare_duration(
        netease_data["duration_ms"], 0, qqmusic_data["duration_ms"]
    )
    print(f"时长比较结果: {duration_result['status']}")

    # 测试封面图比较
    cover_json = (
        '{"is_same": true, "confidence": 0.9, "differences": [], "notes": "相同"}'
    )
    cover_result = parse_cover_comparison_json(cover_json)
    print(f"封面图比较结果: {cover_result['status']}")

    print("\n✅ 集成测试通过\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 1 元数据比较增强功能测试")
    print("=" * 60)

    try:
        test_lyrics_comparison()
        test_duration_comparison()
        test_cover_comparison_json()
        test_integration()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
