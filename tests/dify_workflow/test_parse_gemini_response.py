"""
测试 parse_gemini_response 节点
"""

import sys
import json
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "dify-workflow" / "nodes" / "code-nodes"),
)

from parse_gemini_response import main


class TestParseGeminiResponse:
    """测试 Gemini 响应解析节点"""

    def test_parse_valid_response_with_markdown(self):
        """测试带 markdown 代码块的响应"""
        response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '```json\n{"is_same": false, "confidence": 1.0, "differences": ["差异1", "差异2"], "notes": "测试说明"}\n```'
                            }
                        ]
                    }
                }
            ]
        }

        result = main(json.dumps(response))

        assert result["success"] is True
        assert result["is_same"] is False
        assert result["confidence"] == 1.0
        assert len(result["differences"]) == 2
        assert result["notes"] == "测试说明"
        assert result["error"] == ""

    def test_parse_valid_response_without_markdown(self):
        """测试不带 markdown 代码块的响应"""
        response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{"is_same": true, "confidence": 0.95, "differences": [], "notes": "相同"}'
                            }
                        ]
                    }
                }
            ]
        }

        result = main(json.dumps(response))

        assert result["success"] is True
        assert result["is_same"] is True
        assert result["confidence"] == 0.95
        assert len(result["differences"]) == 0

    def test_parse_dict_input(self):
        """测试字典输入"""
        response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{"is_same": false, "confidence": 0.8, "differences": ["差异"], "notes": ""}'
                            }
                        ]
                    }
                }
            ]
        }

        result = main(response)

        assert result["success"] is True
        assert result["is_same"] is False
        assert result["confidence"] == 0.8

    def test_parse_missing_candidates(self):
        """测试缺少 candidates 字段"""
        response = {"other_field": "value"}

        result = main(json.dumps(response))

        assert result["success"] is False
        assert result["is_same"] is False
        assert result["confidence"] == 0.0

    def test_parse_invalid_json_in_text(self):
        """测试 text 中的无效 JSON"""
        response = {"candidates": [{"content": {"parts": [{"text": "invalid json"}]}}]}

        result = main(json.dumps(response))

        assert result["success"] is False
        assert result["error"] != ""

    def test_parse_empty_response(self):
        """测试空响应"""
        result = main("{}")

        assert result["success"] is False
        assert result["is_same"] is False

    def test_parse_with_complex_differences(self):
        """测试复杂的差异列表"""
        response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "is_same": False,
                                        "confidence": 1.0,
                                        "differences": [
                                            "背景图案和风格完全不同",
                                            "顶部的音乐平台Logo不同",
                                            "整体构图不同",
                                        ],
                                        "notes": "两张专辑封面共享相同的核心项目名称",
                                    }
                                )
                            }
                        ]
                    }
                }
            ]
        }

        result = main(json.dumps(response))

        assert result["success"] is True
        assert len(result["differences"]) == 3
        assert "背景图案" in result["differences"][0]
