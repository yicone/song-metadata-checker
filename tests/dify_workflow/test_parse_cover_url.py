"""
测试 parse_cover_url 节点
"""

import sys
import json
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "dify-workflow" / "nodes" / "code-nodes"),
)

from parse_cover_url import main


class TestParseCoverUrl:
    """测试封面图 URL 解析节点"""

    def test_parse_valid_response(self):
        """测试有效的响应"""
        response = {"imageUrl": "https://example.com/cover.jpg"}

        result = main(json.dumps(response))

        assert result["success"] is True
        assert result["cover_url"] == "https://example.com/cover.jpg"
        assert result["error"] == ""

    def test_parse_dict_input(self):
        """测试字典输入"""
        response = {"imageUrl": "https://example.com/cover2.jpg"}

        result = main(response)

        assert result["success"] is True
        assert result["cover_url"] == "https://example.com/cover2.jpg"

    def test_parse_missing_imageurl(self):
        """测试缺少 imageUrl 字段"""
        response = {"other_field": "value"}

        result = main(json.dumps(response))

        assert result["success"] is True
        assert result["cover_url"] == ""

    def test_parse_empty_response(self):
        """测试空响应"""
        result = main("{}")

        assert result["success"] is True
        assert result["cover_url"] == ""

    def test_parse_invalid_json(self):
        """测试无效的 JSON"""
        result = main("invalid json")

        assert result["success"] is False
        assert result["cover_url"] == ""
        assert result["error"] != ""

    def test_parse_empty_imageurl(self):
        """测试空的 imageUrl"""
        response = {"imageUrl": ""}

        result = main(json.dumps(response))

        assert result["success"] is True
        assert result["cover_url"] == ""
