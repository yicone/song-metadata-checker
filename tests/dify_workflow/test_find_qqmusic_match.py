"""
测试 find_qqmusic_match 节点
"""

import sys
import json
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "dify-workflow" / "nodes" / "code-nodes"),
)

from find_qqmusic_match import main


class TestFindQQMusicMatch:
    """测试 QQ 音乐匹配节点"""

    def test_find_match_with_results(self):
        """测试有搜索结果的情况"""
        search_results = {
            "song": {
                "list": [
                    {
                        "songmid": "000edAg12jLBrN",
                        "songname": "不将就",
                        "albumname": "有理想",
                    }
                ]
            }
        }

        result = main(json.dumps(search_results), "不将就", "李荣浩")

        assert result["match_found"] is True
        assert result["match_id"] == "000edAg12jLBrN"
        assert result["match_name"] == "不将就"
        assert result["match_album"] == "有理想"
        assert result["error"] == ""

    def test_find_match_no_results(self):
        """测试无搜索结果的情况"""
        search_results = {"song": {"list": []}}

        result = main(json.dumps(search_results), "不存在的歌", "不存在的歌手")

        assert result["match_found"] is False
        assert result["match_id"] == ""
        assert result["match_name"] == ""
        assert result["match_album"] == ""
        assert "搜索无结果" in result["error"]

    def test_find_match_dict_input(self):
        """测试字典输入（已解析的数据）"""
        search_results = {
            "song": {
                "list": [
                    {
                        "songmid": "test123",
                        "songname": "测试歌曲",
                        "albumname": "测试专辑",
                    }
                ]
            }
        }

        result = main(search_results, "测试歌曲", "测试歌手")

        assert result["match_found"] is True
        assert result["match_id"] == "test123"

    def test_find_match_invalid_json(self):
        """测试无效的 JSON"""
        result = main("invalid json", "歌曲", "歌手")

        assert result["match_found"] is False
        assert result["error"] != ""

    def test_find_match_missing_song_key(self):
        """测试缺少 song 键的数据"""
        search_results = {"other_key": {}}

        result = main(json.dumps(search_results), "歌曲", "歌手")

        assert result["match_found"] is False
        assert "搜索无结果" in result["error"]

    def test_find_match_multiple_results(self):
        """测试多个搜索结果（应返回第一个）"""
        search_results = {
            "song": {
                "list": [
                    {"songmid": "first", "songname": "第一首", "albumname": "专辑1"},
                    {"songmid": "second", "songname": "第二首", "albumname": "专辑2"},
                ]
            }
        }

        result = main(json.dumps(search_results), "歌曲", "歌手")

        assert result["match_found"] is True
        assert result["match_id"] == "first"
        assert result["match_name"] == "第一首"
