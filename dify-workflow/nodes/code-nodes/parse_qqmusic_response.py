"""
解析 QQ 音乐响应节点
解析 Dify HTTP 节点包装的响应，并平铺输出字段

输入变量:
- qqmusic_song_data - QQ Music 歌曲详情响应（可能是字符串或字典）

输出变量:
- parsed_data: dict - 完整解析后的数据
- track_name: str - 歌曲名称
- track_title: str - 歌曲标题
- album_id: int - 专辑 ID
- album_mid: str - 专辑 MID
- album_name: str - 专辑名称
- album_pmid: str - 专辑封面图 ID
- interval: int - 歌曲时长（秒）
- success: bool - 解析状态
- error: str - 错误信息
"""

import json
from models import ParseQQMusicResponseOutput


def main(qqmusic_response) -> ParseQQMusicResponseOutput:
    """
    解析 QQ 音乐响应并平铺输出字段
    输入可能是字符串或字典
    """
    try:
        # 1. 智能解析（输入可能是字符串或对象）
        if isinstance(qqmusic_response, str):
            qqmusic_parsed = json.loads(qqmusic_response)
        elif isinstance(qqmusic_response, dict):
            # 如果是字典，检查是否有 body 字段（HTTP 节点包装）
            if "body" in qqmusic_response:
                body = qqmusic_response["body"]
                if isinstance(body, str):
                    qqmusic_parsed = json.loads(body)
                else:
                    qqmusic_parsed = body
            else:
                # 直接就是解析后的数据
                qqmusic_parsed = qqmusic_response
        else:
            raise ValueError(f"Unexpected input type: {type(qqmusic_response)}")

        # 2. 提取数据（代理服务器已简化结构）
        # 新版代理返回: {"track_info": {...}, "extras": {...}, "info": {...}}
        # 旧版代理返回: {"response": {"songinfo": {"data": {...}}}}
        if "track_info" in qqmusic_parsed:
            # 新版：直接访问 track_info
            track_info = qqmusic_parsed.get("track_info", {})
        elif "response" in qqmusic_parsed:
            # 旧版：需要嵌套访问
            track_info = (
                qqmusic_parsed.get("response", {})
                .get("songinfo", {})
                .get("data", {})
                .get("track_info", {})
            )
        else:
            # 未知格式
            track_info = {}

        # 4. 平铺输出（Dify Cloud 不支持嵌套访问）
        album_info = track_info.get("album", {})

        output = ParseQQMusicResponseOutput(
            parsed_data=qqmusic_parsed,
            track_name=track_info.get("name", ""),
            track_title=track_info.get("title", ""),
            album_id=album_info.get("id", 0),
            album_mid=album_info.get("mid", ""),
            album_name=album_info.get("name", ""),
            album_pmid=album_info.get("pmid", ""),
            interval=track_info.get("interval", 0),
            success=True,
            error="",
        )
        return output

    except Exception as e:
        output = ParseQQMusicResponseOutput(
            parsed_data={},
            track_name="",
            track_title="",
            album_id=0,
            album_mid="",
            album_name="",
            album_pmid="",
            interval=0,
            success=False,
            error=str(e),
        )
        return output
