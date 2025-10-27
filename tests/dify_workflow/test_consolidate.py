"""
测试 consolidate 节点
"""

import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "dify-workflow" / "nodes" / "code-nodes"),
)

from consolidate import main


class TestConsolidate:
    """测试数据整合与核验节点"""

    def test_basic_consolidation(self):
        """测试基本的数据整合"""
        netease_data = {
            "song_id": "123",
            "song_title": "测试歌曲",
            "artists": ["歌手A"],
            "album": "测试专辑",
            "duration": 180000,  # 3分钟
            "lyrics": {"original": "歌词内容"},
            "cover_url": "https://example.com/cover.jpg",
        }

        result = main(
            netease_data=netease_data,
            qqmusic_track_name="测试歌曲",
            qqmusic_interval=180,
            qqmusic_album_name="测试专辑",
        )

        assert result["success"] is True
        assert result["final_report"]["fields"]["title"]["status"] == "确认"
        assert result["final_report"]["fields"]["album"]["status"] == "确认"
        assert result["final_report"]["fields"]["duration"]["status"] == "确认"

    def test_title_mismatch(self):
        """测试标题不匹配"""
        netease_data = {
            "song_id": "123",
            "song_title": "歌曲A",
            "artists": [],
            "album": "",
            "duration": 0,
            "lyrics": {},
            "cover_url": "",
        }

        result = main(netease_data=netease_data, qqmusic_track_name="歌曲B")

        assert result["success"] is True
        assert result["final_report"]["fields"]["title"]["status"] == "未查到"

    def test_duration_within_tolerance(self):
        """测试时长在容差范围内"""
        netease_data = {
            "song_id": "123",
            "song_title": "歌曲",
            "artists": [],
            "album": "",
            "duration": 180000,  # 180秒 = 3分钟
            "lyrics": {},
            "cover_url": "",
        }

        result = main(
            netease_data=netease_data,
            qqmusic_interval=181,  # 差1秒，在容差内
        )

        assert result["success"] is True
        assert result["final_report"]["fields"]["duration"]["status"] == "确认"

    def test_duration_outside_tolerance(self):
        """测试时长超出容差"""
        netease_data = {
            "song_id": "123",
            "song_title": "歌曲",
            "artists": [],
            "album": "",
            "duration": 180000,  # 180秒
            "lyrics": {},
            "cover_url": "",
        }

        result = main(
            netease_data=netease_data,
            qqmusic_interval=185,  # 差5秒，超出容差
        )

        assert result["success"] is True
        assert result["final_report"]["fields"]["duration"]["status"] == "存疑"

    def test_lyrics_comparison(self):
        """测试歌词比较"""
        netease_data = {
            "song_id": "123",
            "song_title": "歌曲",
            "artists": [],
            "album": "",
            "duration": 0,
            "lyrics": {"original": "[00:01.00]第一行\n[00:02.00]第二行"},
            "cover_url": "",
        }

        qqmusic_parsed_data = {
            "track_info": {"lyric": "[00:01.00]第一行\n[00:02.00]第二行", "singer": []}
        }

        result = main(
            netease_data=netease_data, qqmusic_parsed_data=qqmusic_parsed_data
        )

        assert result["success"] is True
        assert result["final_report"]["fields"]["lyrics"]["status"] == "确认"

    def test_gemini_cover_comparison(self):
        """测试 Gemini 封面图比较"""
        netease_data = {
            "song_id": "123",
            "song_title": "歌曲",
            "artists": [],
            "album": "",
            "duration": 0,
            "lyrics": {},
            "cover_url": "https://example.com/cover.jpg",
        }

        result = main(
            netease_data=netease_data,
            gemini_is_same=True,
            gemini_confidence=0.95,
            gemini_differences=[],
            gemini_notes="封面图相同",
        )

        assert result["success"] is True
        assert result["final_report"]["fields"]["cover_art"]["status"] == "确认"
        assert (
            result["final_report"]["fields"]["cover_art"]["ai_comparison"]["is_same"]
            is True
        )

    def test_gemini_cover_different(self):
        """测试 Gemini 判断封面图不同"""
        netease_data = {
            "song_id": "123",
            "song_title": "歌曲",
            "artists": [],
            "album": "",
            "duration": 0,
            "lyrics": {},
            "cover_url": "https://example.com/cover.jpg",
        }

        result = main(
            netease_data=netease_data,
            gemini_is_same=False,
            gemini_confidence=1.0,
            gemini_differences=["背景不同", "Logo不同"],
            gemini_notes="封面图不同",
        )

        assert result["success"] is True
        assert result["final_report"]["fields"]["cover_art"]["status"] == "存疑"
        assert (
            len(
                result["final_report"]["fields"]["cover_art"]["ai_comparison"][
                    "differences"
                ]
            )
            == 2
        )

    def test_summary_calculation(self):
        """测试摘要统计"""
        netease_data = {
            "song_id": "123",
            "song_title": "歌曲",
            "artists": ["歌手"],
            "album": "专辑",
            "duration": 180000,
            "lyrics": {},
            "cover_url": "",
        }

        result = main(
            netease_data=netease_data,
            qqmusic_track_name="歌曲",
            qqmusic_album_name="专辑",
            qqmusic_interval=180,
        )

        assert result["success"] is True
        summary = result["final_report"]["summary"]
        assert (
            summary["total_fields"] == 6
        )  # title, artists, album, duration, lyrics, cover_art
        assert summary["confirmed"] >= 3  # title, album, duration
        assert 0 <= summary["confidence_score"] <= 1

    def test_error_handling(self):
        """测试错误处理"""
        # 传入 None 应该能处理
        result = main(netease_data=None)

        assert result["success"] is False
        assert result["error"] != ""

    def test_artists_comparison(self):
        """测试艺术家比较"""
        netease_data = {
            "song_id": "123",
            "song_title": "歌曲",
            "artists": ["歌手A", "歌手B"],
            "album": "",
            "duration": 0,
            "lyrics": {},
            "cover_url": "",
        }

        qqmusic_parsed_data = {
            "track_info": {"singer": [{"name": "歌手A"}, {"name": "歌手B"}]}
        }

        result = main(
            netease_data=netease_data, qqmusic_parsed_data=qqmusic_parsed_data
        )

        assert result["success"] is True
        assert result["final_report"]["fields"]["artists"]["status"] == "确认"
