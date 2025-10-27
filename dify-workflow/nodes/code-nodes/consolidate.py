"""
数据整合与核验节点 (Phase 1 增强版)
整合多源数据并生成核验报告

输入变量:
- netease_data: dict - 网易云音乐数据
- qqmusic_track_name: str - QQ 音乐歌曲名称（平铺字段）
- qqmusic_interval: int - QQ 音乐时长（秒）
- qqmusic_album_name: str - QQ 音乐专辑名称
- qqmusic_parsed_data: dict - QQ 音乐完整数据
- gemini_is_same: bool - Gemini 封面图比较结果
- gemini_confidence: float - Gemini 置信度
- gemini_differences: list - Gemini 差异列表
- gemini_notes: str - Gemini 额外说明

输出变量:
- final_report: dict - 完整核验报告
- success: bool - 执行状态
- error: str - 错误信息
"""

import re
from difflib import SequenceMatcher
from typing import Dict, Any, Optional, List
from models import ConsolidateOutput


def main(
    netease_data: Dict[str, Any],
    qqmusic_track_name: str = "",
    qqmusic_interval: int = 0,
    qqmusic_album_name: str = "",
    qqmusic_parsed_data: Optional[Dict[str, Any]] = None,
    gemini_is_same: Optional[bool] = None,
    gemini_confidence: Optional[float] = None,
    gemini_differences: Optional[List[str]] = None,
    gemini_notes: Optional[str] = None,
) -> ConsolidateOutput:
    """
    整合多源数据并生成核验报告 (Phase 1 增强版)
    使用平铺字段，避免 Dify Cloud 嵌套访问限制
    使用 Gemini AI 的封面图比较结果
    """
    try:
        fields = {}

        # 1. 核验标题（使用平铺字段）
        netease_title = netease_data.get("song_title", "")
        fields["title"] = {"value": netease_title, "status": "未查到"}

        if qqmusic_track_name:
            if qqmusic_track_name.lower() == netease_title.lower():
                fields["title"]["status"] = "确认"
                fields["title"]["confirmed_by"] = ["QQ Music"]

        # 2. 核验艺术家（使用完整数据）
        netease_artists = netease_data.get("artists", [])
        fields["artists"] = {"value": netease_artists, "status": "未查到"}

        if qqmusic_parsed_data:
            # 兼容新旧两种数据格式
            if "track_info" in qqmusic_parsed_data:
                # 新版代理：直接访问
                track_info = qqmusic_parsed_data.get("track_info", {})
            else:
                # 旧版代理：嵌套访问
                track_info = (
                    qqmusic_parsed_data.get("response", {})
                    .get("songinfo", {})
                    .get("data", {})
                    .get("track_info", {})
                )

            qqmusic_artists = [s.get("name", "") for s in track_info.get("singer", [])]
            if qqmusic_artists and set(qqmusic_artists) == set(netease_artists):
                fields["artists"]["status"] = "确认"
                fields["artists"]["confirmed_by"] = ["QQ Music"]

        # 3. 核验专辑（使用平铺字段）
        netease_album = netease_data.get("album", "")
        fields["album"] = {"value": netease_album, "status": "未查到"}

        if qqmusic_album_name:
            if qqmusic_album_name.lower() == netease_album.lower():
                fields["album"]["status"] = "确认"
                fields["album"]["confirmed_by"] = ["QQ Music"]

        # 4. 核验时长 (Phase 1 - 使用平铺字段)
        netease_duration = netease_data.get("duration", 0)
        fields["duration"] = {
            "value": netease_duration,
            "value_formatted": f"{netease_duration // 60000}:{(netease_duration % 60000) // 1000:02d}"
            if netease_duration
            else "0:00",
            "status": "未查到",
        }

        if qqmusic_interval and netease_duration:
            qqmusic_duration = qqmusic_interval * 1000  # 秒转毫秒
            diff = abs(netease_duration - qqmusic_duration)
            if diff <= 2000:  # ±2秒容差
                fields["duration"]["status"] = "确认"
                fields["duration"]["confirmed_by"] = ["QQ Music"]
            else:
                fields["duration"]["status"] = "存疑"
                fields["duration"]["note"] = f"时长差异 {diff // 1000} 秒"

        # 5. 核验歌词 (Phase 1 - 使用完整数据)
        netease_lyrics = netease_data.get("lyrics", {})
        netease_lyrics_text = (
            netease_lyrics.get("original", "")
            if isinstance(netease_lyrics, dict)
            else ""
        )
        fields["lyrics"] = {
            "value": netease_lyrics_text[:100] + "..."
            if len(netease_lyrics_text) > 100
            else netease_lyrics_text,
            "status": "未查到",
        }

        if netease_lyrics_text and qqmusic_parsed_data:
            # 预处理歌词：去除时间戳和标点
            def clean_lyrics(text):
                text = re.sub(r"\[\d+:\d+\.\d+\]", "", text)  # 去除时间戳
                text = "\n".join(
                    [line.strip() for line in text.split("\n") if line.strip()]
                )
                return text.lower().strip()

            netease_clean = clean_lyrics(netease_lyrics_text)

            # 兼容新旧两种数据格式
            if "track_info" in qqmusic_parsed_data:
                # 新版代理：直接访问
                track_info = qqmusic_parsed_data.get("track_info", {})
            else:
                # 旧版代理：嵌套访问
                track_info = (
                    qqmusic_parsed_data.get("response", {})
                    .get("songinfo", {})
                    .get("data", {})
                    .get("track_info", {})
                )

            qqmusic_lyrics_text = track_info.get("lyric", "")

            if qqmusic_lyrics_text:
                qqmusic_clean = clean_lyrics(qqmusic_lyrics_text)
                similarity = SequenceMatcher(None, netease_clean, qqmusic_clean).ratio()
                fields["lyrics"]["similarity_score"] = similarity

                if similarity >= 0.95:
                    fields["lyrics"]["status"] = "确认"
                    fields["lyrics"]["confirmed_by"] = ["QQ Music"]
                elif similarity >= 0.80:
                    fields["lyrics"]["status"] = "存疑"
                    fields["lyrics"]["note"] = f"相似度 {similarity:.2%}"

        # 6. 核验封面图 (Phase 1 增强 - 使用 Gemini AI)
        fields["cover_art"] = {
            "value": netease_data.get("cover_url", ""),
            "status": "未查到",
        }

        if gemini_is_same is not None:
            # 使用 Gemini 解析后的结果
            if gemini_is_same and gemini_confidence and gemini_confidence > 0.8:
                fields["cover_art"]["status"] = "确认"
            else:
                fields["cover_art"]["status"] = "存疑"

            fields["cover_art"]["ai_comparison"] = {
                "is_same": gemini_is_same,
                "confidence": gemini_confidence or 0.0,
                "differences": gemini_differences or [],
                "notes": gemini_notes or "",
            }

        # 生成摘要
        confirmed = sum(1 for f in fields.values() if f.get("status") == "确认")
        questionable = sum(1 for f in fields.values() if f.get("status") == "存疑")
        not_found = sum(1 for f in fields.values() if f.get("status") == "未查到")

        # 收集各平台原始值（用于人工核验）
        raw_values = {
            "netease": {
                "title": netease_data.get("song_title", ""),
                "artists": netease_data.get("artists", []),
                "album": netease_data.get("album", ""),
                "duration_ms": netease_data.get("duration", 0),
                "lyrics_preview": netease_lyrics_text[:100] + "..."
                if len(netease_lyrics_text) > 100
                else netease_lyrics_text,
                "cover_url": netease_data.get("cover_url", ""),
            }
        }

        # 添加 QQ Music 原始值（如果有）
        if qqmusic_parsed_data:
            # 兼容新旧两种数据格式
            if "track_info" in qqmusic_parsed_data:
                track_info = qqmusic_parsed_data.get("track_info", {})
            else:
                track_info = (
                    qqmusic_parsed_data.get("response", {})
                    .get("songinfo", {})
                    .get("data", {})
                    .get("track_info", {})
                )

            raw_values["qqmusic"] = {
                "title": track_info.get("name", ""),
                "artists": [s.get("name", "") for s in track_info.get("singer", [])],
                "album": track_info.get("album", {}).get("name", ""),
                "duration_sec": track_info.get("interval", 0),
                "lyrics_preview": track_info.get("lyric", "")[:100] + "..."
                if len(track_info.get("lyric", "")) > 100
                else track_info.get("lyric", ""),
                "album_pmid": track_info.get("album", {}).get("pmid", ""),
            }

        report = {
            "metadata": {
                "song_id": netease_data.get("song_id", ""),
                "source": "NetEase Cloud Music",
                "verified_with": ["QQ Music"] if qqmusic_parsed_data else [],
            },
            "raw_values": raw_values,
            "fields": fields,
            "summary": {
                "total_fields": len(fields),
                "confirmed": confirmed,
                "questionable": questionable,
                "not_found": not_found,
                "confidence_score": confirmed / len(fields) if fields else 0,
            },
        }

        output = ConsolidateOutput(final_report=report, success=True, error="")
        return output

    except Exception as e:
        output = ConsolidateOutput(final_report={}, success=False, error=str(e))
        return output
