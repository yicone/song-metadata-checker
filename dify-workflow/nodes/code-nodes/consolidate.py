"""
数据整合与核验节点
比对多源数据并生成最终核验报告

输入变量:
- normalized_data: dict - 规范化后的数据
- cover_match_result: str - 封面图比对结果

输出变量:
- final_report: dict - 最终核验报告 JSON
"""

from difflib import SequenceMatcher


def similarity_ratio(a: str, b: str) -> float:
    """计算字符串相似度"""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def compare_field(
    netease_value, spotify_value, qqmusic_value, field_type="string"
) -> dict:
    """
    比较单个字段的值
    返回核验状态和详细信息
    """
    result = {"value": netease_value, "status": "未查到", "sources": {}}

    # 如果网易云值为空
    if not netease_value:
        result["status"] = "未查到"
        return result

    # 字符串类型比较
    if field_type == "string":
        spotify_match = False
        qqmusic_match = False

        if spotify_value:
            result["sources"]["spotify"] = spotify_value
            ratio = similarity_ratio(str(netease_value), str(spotify_value))
            if ratio >= 0.95:  # 几乎完全匹配
                spotify_match = True
            elif ratio >= 0.8:  # 相似但有差异
                result["status"] = "存疑"
                result["note"] = f"与 Spotify 数据相似但有差异 (相似度: {ratio:.2%})"

        if qqmusic_value:
            result["sources"]["qqmusic"] = qqmusic_value
            ratio = similarity_ratio(str(netease_value), str(qqmusic_value))
            if ratio >= 0.95:
                qqmusic_match = True
            elif ratio >= 0.8 and result["status"] != "存疑":
                result["status"] = "存疑"
                result["note"] = f"与 QQ 音乐数据相似但有差异 (相似度: {ratio:.2%})"

        # 如果至少一个源完全匹配
        if spotify_match or qqmusic_match:
            result["status"] = "确认"
            result["confirmed_by"] = []
            if spotify_match:
                result["confirmed_by"].append("Spotify")
            if qqmusic_match:
                result["confirmed_by"].append("QQ音乐")

        # 如果两个源都有数据但都不匹配
        elif spotify_value and qqmusic_value and result["status"] != "存疑":
            result["status"] = "存疑"
            result["note"] = "多个数据源结果不一致"

    # 列表类型比较（如歌手列表）
    elif field_type == "list":
        if not isinstance(netease_value, list):
            netease_value = [netease_value]

        spotify_match = False
        qqmusic_match = False

        if spotify_value and isinstance(spotify_value, list):
            result["sources"]["spotify"] = spotify_value
            # 检查是否有重叠
            overlap = set(netease_value) & set(spotify_value)
            if overlap == set(netease_value):  # 完全匹配
                spotify_match = True
            elif overlap:  # 部分匹配
                result["status"] = "存疑"
                result["note"] = f"与 Spotify 数据部分匹配 (匹配: {list(overlap)})"

        if qqmusic_value and isinstance(qqmusic_value, list):
            result["sources"]["qqmusic"] = qqmusic_value
            overlap = set(netease_value) & set(qqmusic_value)
            if overlap == set(netease_value):
                qqmusic_match = True
            elif overlap and result["status"] != "存疑":
                result["status"] = "存疑"
                result["note"] = f"与 QQ 音乐数据部分匹配 (匹配: {list(overlap)})"

        if spotify_match or qqmusic_match:
            result["status"] = "确认"
            result["confirmed_by"] = []
            if spotify_match:
                result["confirmed_by"].append("Spotify")
            if qqmusic_match:
                result["confirmed_by"].append("QQ音乐")

    # 如果所有源都没有数据
    if not spotify_value and not qqmusic_value:
        result["status"] = "未查到"
        result["note"] = "所有核验源均未找到该字段"

    return result


def compare_lyrics(
    netease_lyrics: dict, spotify_lyrics: str, qqmusic_lyrics: str
) -> dict:
    """
    比较歌词内容

    参数:
    - netease_lyrics: dict - {'original': str, 'translated': str}
    - spotify_lyrics: str - 完整歌词文本
    - qqmusic_lyrics: str - 完整歌词文本

    返回:
    - status: '确认' | '存疑' | '未查到'
    - similarity_score: float - 相似度分数
    """
    import re

    result = {
        "value": netease_lyrics.get("original", "")
        if isinstance(netease_lyrics, dict)
        else "",
        "status": "未查到",
        "sources": {},
    }

    # 提取网易云原文歌词
    netease_text = (
        netease_lyrics.get("original", "") if isinstance(netease_lyrics, dict) else ""
    )
    if not netease_text:
        result["note"] = "网易云无歌词"
        return result

    # 预处理：去除时间戳、空行、标点
    def preprocess_lyrics(text: str) -> str:
        if not text:
            return ""
        # 去除时间戳 [00:00.00]
        text = re.sub(r"\[\d+:\d+\.\d+\]", "", text)
        # 去除空行
        text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
        # 统一标点
        text = (
            text.replace("，", ",")
            .replace("。", ".")
            .replace("！", "!")
            .replace("？", "?")
        )
        return text.lower().strip()

    netease_clean = preprocess_lyrics(netease_text)

    max_similarity = 0.0
    confirmed_by = []

    # 比较 Spotify 歌词
    if spotify_lyrics:
        result["sources"]["spotify"] = (
            spotify_lyrics[:100] + "..."
            if len(spotify_lyrics) > 100
            else spotify_lyrics
        )
        spotify_clean = preprocess_lyrics(spotify_lyrics)

        # 计算相似度
        similarity = SequenceMatcher(None, netease_clean, spotify_clean).ratio()
        max_similarity = max(max_similarity, similarity)

        if similarity >= 0.95:
            confirmed_by.append("Spotify")
        elif similarity >= 0.80:
            if result["status"] != "确认":
                result["status"] = "存疑"
                result["note"] = (
                    f"与 Spotify 歌词相似但有差异 (相似度: {similarity:.2%})"
                )

    # 比较 QQ 音乐歌词
    if qqmusic_lyrics:
        result["sources"]["qqmusic"] = (
            qqmusic_lyrics[:100] + "..."
            if len(qqmusic_lyrics) > 100
            else qqmusic_lyrics
        )
        qqmusic_clean = preprocess_lyrics(qqmusic_lyrics)

        similarity = SequenceMatcher(None, netease_clean, qqmusic_clean).ratio()
        max_similarity = max(max_similarity, similarity)

        if similarity >= 0.95:
            confirmed_by.append("QQ音乐")
        elif similarity >= 0.80 and result["status"] != "确认":
            result["status"] = "存疑"
            result["note"] = f"与 QQ 音乐歌词相似但有差异 (相似度: {similarity:.2%})"

    # 设置最终状态
    if confirmed_by:
        result["status"] = "确认"
        result["confirmed_by"] = confirmed_by
        result["similarity_score"] = max_similarity
    elif not spotify_lyrics and not qqmusic_lyrics:
        result["status"] = "未查到"
        result["note"] = "其他平台均无歌词数据"

    if max_similarity > 0:
        result["similarity_score"] = max_similarity

    return result


def compare_duration(netease_ms: int, spotify_ms: int, qqmusic_ms: int) -> dict:
    """
    比较歌曲时长
    允许 ±2 秒的误差（不同平台可能有淡入淡出差异）
    """
    tolerance_ms = 2000  # 2 秒

    result = {
        "value": netease_ms,
        "value_formatted": f"{netease_ms // 60000}:{(netease_ms % 60000) // 1000:02d}"
        if netease_ms
        else "0:00",
        "status": "未查到",
        "sources": {},
    }

    if not netease_ms:
        result["note"] = "网易云未提供时长"
        return result

    matches = []

    if spotify_ms:
        result["sources"]["spotify"] = (
            f"{spotify_ms // 60000}:{(spotify_ms % 60000) // 1000:02d}"
        )
        diff = abs(netease_ms - spotify_ms)
        if diff <= tolerance_ms:
            matches.append("Spotify")
        else:
            result["sources"]["spotify_diff"] = f"差异 {diff // 1000} 秒"

    if qqmusic_ms:
        result["sources"]["qqmusic"] = (
            f"{qqmusic_ms // 60000}:{(qqmusic_ms % 60000) // 1000:02d}"
        )
        diff = abs(netease_ms - qqmusic_ms)
        if diff <= tolerance_ms:
            matches.append("QQ音乐")
        else:
            result["sources"]["qqmusic_diff"] = f"差异 {diff // 1000} 秒"

    if matches:
        result["status"] = "确认"
        result["confirmed_by"] = matches
    elif spotify_ms or qqmusic_ms:
        result["status"] = "存疑"
        result["note"] = "时长差异超过 2 秒"
    else:
        result["status"] = "未查到"
        result["note"] = "其他平台均未提供时长"

    return result


def parse_cover_comparison_json(gemini_response: str) -> dict:
    """
    解析 Gemini 封面比较的 JSON 响应
    如果 JSON 解析失败，回退到文本解析
    """
    import json
    import re

    try:
        # 尝试提取 JSON（Gemini 可能包含额外文本）
        json_match = re.search(r"\{.*\}", gemini_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            is_same = data.get("is_same", False)
            confidence = data.get("confidence", 0.0)

            return {
                "status": "确认" if is_same and confidence > 0.8 else "存疑",
                "confidence": confidence,
                "differences": data.get("differences", []),
                "notes": data.get("notes", ""),
                "is_same": is_same,
            }
    except (json.JSONDecodeError, KeyError, AttributeError):
        pass

    # Fallback 到文本解析
    result_lower = gemini_response.lower().strip()
    if "相同" in result_lower or "same" in result_lower or "yes" in result_lower:
        return {
            "status": "确认",
            "confidence": 0.9,
            "notes": gemini_response,
            "is_same": True,
        }
    elif (
        "不相同" in result_lower or "different" in result_lower or "no" in result_lower
    ):
        return {
            "status": "存疑",
            "confidence": 0.5,
            "notes": gemini_response,
            "is_same": False,
        }
    else:
        return {
            "status": "未查到",
            "confidence": 0.0,
            "notes": gemini_response,
            "is_same": False,
        }


def compare_credits(
    netease_credits: dict, spotify_credits: dict, qqmusic_credits: dict
) -> dict:
    """
    比较制作人员信息
    """
    result = {}

    # 获取所有可能的字段
    all_fields = (
        set(netease_credits.keys())
        | set(spotify_credits.keys())
        | set(qqmusic_credits.keys())
    )

    for field in all_fields:
        netease_value = netease_credits.get(field)
        spotify_value = spotify_credits.get(field)
        qqmusic_value = qqmusic_credits.get(field)

        result[field] = compare_field(
            netease_value, spotify_value, qqmusic_value, "list"
        )

    return result


def main(normalized_data: dict, cover_match_result: str) -> dict:
    """
    整合多源数据并生成最终核验报告
    """
    try:
        netease = normalized_data.get("netease", {})
        spotify = normalized_data.get("spotify", {})
        qqmusic = normalized_data.get("qqmusic", {})

        # 构建最终报告
        report = {
            "metadata": {
                "song_id": netease.get("song_id", ""),
                "source": "NetEase Cloud Music",
                "verification_timestamp": None,  # 可以添加时间戳
            },
            "fields": {},
        }

        # 比较歌曲标题
        report["fields"]["title"] = compare_field(
            netease.get("title"), spotify.get("title"), qqmusic.get("title"), "string"
        )

        # 比较歌手
        report["fields"]["artists"] = compare_field(
            netease.get("artists"),
            spotify.get("artists"),
            qqmusic.get("artists"),
            "list",
        )

        # 比较专辑
        report["fields"]["album"] = compare_field(
            netease.get("album"), spotify.get("album"), qqmusic.get("album"), "string"
        )

        # 比较时长
        report["fields"]["duration"] = compare_duration(
            netease.get("duration_ms", 0),
            spotify.get("duration_ms", 0),
            qqmusic.get("duration_ms", 0),
        )

        # 比较歌词
        report["fields"]["lyrics"] = compare_lyrics(
            netease.get("lyrics", {}),
            spotify.get("lyrics", ""),
            qqmusic.get("lyrics", ""),
        )

        # 封面图核验（增强版）
        cover_comparison = (
            parse_cover_comparison_json(cover_match_result)
            if cover_match_result
            else {}
        )

        report["fields"]["cover_art"] = {
            "value": netease.get("cover_url"),
            "status": cover_comparison.get("status", "未查到"),
            "sources": {
                "spotify": spotify.get("cover_url"),
                "qqmusic": qqmusic.get("cover_url"),
            },
            "ai_comparison": {
                "raw_response": cover_match_result,
                "is_same": cover_comparison.get("is_same", False),
                "confidence": cover_comparison.get("confidence", 0.0),
                "differences": cover_comparison.get("differences", []),
                "notes": cover_comparison.get("notes", ""),
            },
        }

        # 比较制作人员信息
        report["fields"]["credits"] = compare_credits(
            netease.get("credits", {}),
            spotify.get("credits", {}),
            qqmusic.get("credits", {}),
        )

        # 生成摘要统计
        total_fields = 0
        confirmed_fields = 0
        questionable_fields = 0
        not_found_fields = 0

        def count_status(field_data):
            nonlocal \
                total_fields, \
                confirmed_fields, \
                questionable_fields, \
                not_found_fields
            if isinstance(field_data, dict):
                if "status" in field_data:
                    total_fields += 1
                    status = field_data["status"]
                    if status == "确认":
                        confirmed_fields += 1
                    elif status == "存疑":
                        questionable_fields += 1
                    elif status == "未查到":
                        not_found_fields += 1
                else:
                    # 递归处理嵌套字段（如 credits）
                    for value in field_data.values():
                        count_status(value)

        for field_data in report["fields"].values():
            count_status(field_data)

        report["summary"] = {
            "total_fields": total_fields,
            "confirmed": confirmed_fields,
            "questionable": questionable_fields,
            "not_found": not_found_fields,
            "confidence_score": confirmed_fields / total_fields
            if total_fields > 0
            else 0,
        }

        return {"final_report": report, "success": True, "error": None}

    except Exception as e:
        return {
            "final_report": None,
            "success": False,
            "error": f"数据整合失败: {str(e)}",
        }
