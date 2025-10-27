"""
找到 QQ 音乐匹配节点
从搜索结果中找到最佳匹配

输入变量:
- search_results: str - QQ Music 搜索结果
- target_title: str - 目标歌曲标题
- target_artists: str - 目标艺术家

输出变量:
- match_id: str - 匹配的歌曲 MID
- match_name: str - 匹配的歌曲名称
- match_album: str - 匹配的专辑名称
- match_found: bool - 是否找到匹配
- error: str - 错误信息
"""

import json
from models import FindQQMusicMatchOutput


def main(
    qqmusic_search_results, netease_title: str, netease_artist: str
) -> FindQQMusicMatchOutput:
    """
    从搜索结果中找到最佳匹配
    """
    try:
        # 调试：输出输入类型
        print(f"[DEBUG] qqmusic_search_results 类型: {type(qqmusic_search_results)}")
        print(
            f"[DEBUG] qqmusic_search_results 前100字符: {str(qqmusic_search_results)[:100]}"
        )

        # QQ Music API 返回的 body 可能是 JSON 字符串或已解析的 dict
        if isinstance(qqmusic_search_results, str):
            search_data = json.loads(qqmusic_search_results)
        else:
            search_data = qqmusic_search_results

        # 调试：输出数据结构的键
        print(f"[DEBUG] search_data 类型: {type(search_data)}")
        print(
            f"[DEBUG] search_data 顶层键: {list(search_data.keys()) if isinstance(search_data, dict) else 'NOT A DICT'}"
        )

        # 提取搜索结果列表
        # ⚠️ 注意：代理服务器已经提取了 response.data，所以直接访问 song.list
        # 上游 API: response.data.song.list
        # 代理返回: song.list (已去除 response.data 层级)
        song = search_data.get("song", {})
        print(
            f"[DEBUG] song 键: {list(song.keys()) if isinstance(song, dict) else 'NOT A DICT'}"
        )

        results = song.get("list", [])
        print(f"[DEBUG] 搜索结果数量: {len(results)}")

        if results:
            print(
                f"[DEBUG] 第一个结果: {json.dumps(results[0], ensure_ascii=False)[:200]}"
            )

        if not results:
            output = FindQQMusicMatchOutput(
                match_id="",
                match_name="",
                match_album="",
                match_found=False,
                error="搜索无结果",
            )
            return output

        # 简单匹配：取第一个结果
        # TODO: 实现更复杂的匹配算法（比较歌名和艺术家相似度）
        best_match = results[0]

        output = FindQQMusicMatchOutput(
            match_id=best_match.get("songmid", ""),
            match_name=best_match.get("songname", ""),
            match_album=best_match.get("albumname", ""),
            match_found=True,
            error="",
        )
        return output

    except Exception as e:
        output = FindQQMusicMatchOutput(
            match_id="", match_name="", match_album="", match_found=False, error=str(e)
        )
        return output
