"""
初始数据结构化节点
从网易云音乐 API 响应中提取并结构化元数据

输入变量:
- netease_song_details: str - 网易云歌曲详情 JSON 字符串
- netease_lyrics_data: str - 网易云歌词 JSON 字符串

输出变量:
- metadata: dict - 结构化的元数据对象
"""

import json


def main(netease_song_details: str, netease_lyrics_data: str) -> dict:
    """
    从网易云音乐 API 响应中提取并结构化元数据
    """
    try:
        # 解析 JSON 响应
        song_data = json.loads(netease_song_details)
        lyrics_data = json.loads(netease_lyrics_data)
        
        # 提取歌曲信息
        songs = song_data.get('songs', [])
        if not songs:
            return {
                'metadata': None,
                'success': False,
                'error': '未找到歌曲信息'
            }
        
        song = songs[0]
        
        # 提取歌手信息
        artists = song.get('ar', [])
        artist_names = [artist.get('name', '') for artist in artists]
        
        # 提取专辑信息
        album = song.get('al', {})
        
        # 提取歌词
        lrc = lyrics_data.get('lrc', {})
        lyric_text = lrc.get('lyric', '')
        
        # 提取翻译歌词（如果有）
        tlyric = lyrics_data.get('tlyric', {})
        translated_lyric = tlyric.get('lyric', '')
        
        # 构建结构化元数据
        metadata = {
            'song_id': str(song.get('id', '')),
            'song_title': song.get('name', ''),
            'artists': artist_names,
            'album_name': album.get('name', ''),
            'album_id': str(album.get('id', '')),
            'cover_art_url': album.get('picUrl', ''),
            'lyrics': {
                'original': lyric_text,
                'translated': translated_lyric
            },
            'duration_ms': song.get('dt', 0),
            'publish_time': album.get('publishTime', 0),
            # 制作人员信息将在 OCR 阶段填充
            'credits': {},
            # 核验状态将在后续阶段填充
            'verification': {}
        }
        
        return {
            'metadata': metadata,
            'success': True,
            'error': None
        }
    
    except json.JSONDecodeError as e:
        return {
            'metadata': None,
            'success': False,
            'error': f'JSON 解析失败: {str(e)}'
        }
    except Exception as e:
        return {
            'metadata': None,
            'success': False,
            'error': f'数据结构化失败: {str(e)}'
        }
