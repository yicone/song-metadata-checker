"""
测试 parse_url 节点
"""

import sys
from pathlib import Path

# 添加 dify-workflow/nodes/code-nodes 到 Python 路径
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "dify-workflow" / "nodes" / "code-nodes"),
)

from parse_url import main


class TestParseUrl:
    """测试 URL 解析节点"""

    def test_parse_url_with_hash(self):
        """测试带 # 的 URL"""
        url = "https://music.163.com#/song?id=2758218600"
        result = main(url)

        assert result["success"] is True
        assert result["song_id"] == "2758218600"
        assert result["error"] == ""

    def test_parse_url_without_hash(self):
        """测试不带 # 的 URL"""
        url = "https://music.163.com/song?id=2758218600"
        result = main(url)

        assert result["success"] is True
        assert result["song_id"] == "2758218600"
        assert result["error"] == ""

    def test_parse_url_with_hash_slash(self):
        """测试带 #/ 的 URL"""
        url = "https://music.163.com/#/song?id=2758218600"
        result = main(url)

        assert result["success"] is True
        assert result["song_id"] == "2758218600"
        assert result["error"] == ""

    def test_parse_url_missing_id(self):
        """测试缺少 id 参数的 URL"""
        url = "https://music.163.com/song"
        result = main(url)

        assert result["success"] is False
        assert result["song_id"] is None
        assert "id 参数" in result["error"]

    def test_parse_url_invalid_format(self):
        """测试无效的 URL 格式"""
        url = "not-a-valid-url"
        result = main(url)

        # 应该能处理，但找不到 id
        assert result["success"] is False
        assert result["song_id"] is None

    def test_parse_url_empty_string(self):
        """测试空字符串"""
        url = ""
        result = main(url)

        assert result["success"] is False
        assert result["song_id"] is None
