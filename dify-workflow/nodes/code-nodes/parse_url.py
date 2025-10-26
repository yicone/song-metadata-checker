"""
URL 解析节点
从网易云音乐 URL 中提取歌曲 ID

输入变量:
- song_url: str - 网易云音乐歌曲页面 URL

输出变量:
- song_id: str - 提取的歌曲 ID
"""

from urllib.parse import urlparse, parse_qs


def main(song_url: str) -> dict:
    """
    从网易云音乐 URL 中提取歌曲 ID
    
    支持的 URL 格式:
    - https://music.163.com#/song?id=2758218600
    - https://music.163.com/song?id=2758218600
    - https://music.163.com/#/song?id=2758218600
    """
    try:
        # 处理带 # 的 URL
        if '#' in song_url:
            # 分割 URL，取 # 后面的部分
            fragment_part = song_url.split('#')[-1]
            # 如果 fragment 以 / 开头，去掉它
            if fragment_part.startswith('/'):
                fragment_part = fragment_part[1:]
            # 重新构造 URL 用于解析
            parsed_url = urlparse(f"http://dummy.com/{fragment_part}")
        else:
            parsed_url = urlparse(song_url)
        
        # 解析查询参数
        query_params = parse_qs(parsed_url.query)
        
        # 提取 id 参数
        if 'id' in query_params:
            song_id = query_params['id'][0]
            return {
                'song_id': song_id,
                'success': True,
                'error': None
            }
        else:
            return {
                'song_id': None,
                'success': False,
                'error': 'URL 中未找到 id 参数'
            }
    
    except Exception as e:
        return {
            'song_id': None,
            'success': False,
            'error': f'URL 解析失败: {str(e)}'
        }
