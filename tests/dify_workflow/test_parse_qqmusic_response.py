"""
测试 parse_qqmusic_response 节点
"""

import sys
import json
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "dify-workflow" / "nodes" / "code-nodes"),
)

from parse_qqmusic_response import main


class TestParseQQMusicResponse:
    """测试 QQ 音乐响应解析节点"""

    def test_parse_new_format(self):
        """测试新版代理格式"""
        response = {
            "track_info": {
                "name": "不将就",
                "title": "不将就",
                "interval": 312,
                "album": {
                    "id": 1276189,
                    "mid": "001fi1zG0EjU2u",
                    "name": "有理想",
                    "pmid": "001fi1zG0EjU2u",
                },
            }
        }

        result = main(json.dumps(response))

        assert result["success"] is True
        assert result["track_name"] == "不将就"
        assert result["track_title"] == "不将就"
        assert result["interval"] == 312
        assert result["album_name"] == "有理想"
        assert result["album_pmid"] == "001fi1zG0EjU2u"
        assert result["error"] == ""

    def test_parse_old_format(self):
        """测试旧版代理格式"""
        response = {
            "response": {
                "songinfo": {
                    "data": {
                        "track_info": {
                            "name": "测试歌曲",
                            "interval": 200,
                            "album": {"name": "测试专辑", "pmid": "test_pmid"},
                        }
                    }
                }
            }
        }

        result = main(json.dumps(response))

        assert result["success"] is True
        assert result["track_name"] == "测试歌曲"
        assert result["interval"] == 200
        assert result["album_name"] == "测试专辑"

    def test_parse_dict_input(self):
        """测试字典输入"""
        response = {
            "track_info": {
                "name": "字典输入",
                "interval": 180,
                "album": {"name": "专辑"},
            }
        }

        result = main(response)

        assert result["success"] is True
        assert result["track_name"] == "字典输入"

    def test_parse_with_body_wrapper(self):
        """测试带 body 包装的输入"""
        response = {
            "body": json.dumps(
                {
                    "track_info": {
                        "name": "包装测试",
                        "interval": 150,
                        "album": {"name": "专辑"},
                    }
                }
            ),
            "status_code": 200,
        }

        result = main(response)

        assert result["success"] is True
        assert result["track_name"] == "包装测试"

    def test_parse_invalid_json(self):
        """测试无效的 JSON"""
        result = main("invalid json")

        assert result["success"] is False
        assert result["track_name"] == ""
        assert result["error"] != ""

    def test_parse_empty_response(self):
        """测试空响应"""
        result = main("{}")

        assert result["success"] is True
        assert result["track_name"] == ""
        assert result["interval"] == 0

    def test_parse_missing_fields(self):
        """测试缺少字段的响应"""
        response = {
            "track_info": {
                "name": "只有名称"
                # 缺少 interval, album 等
            }
        }

        result = main(json.dumps(response))

        assert result["success"] is True
        assert result["track_name"] == "只有名称"
        assert result["interval"] == 0
        assert result["album_name"] == ""
