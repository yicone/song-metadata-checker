"""
数据规范化节点
规范化来自不同平台的元数据以便比较

输入变量:
- netease_data: dict - 网易云数据
- spotify_data: str - Spotify 数据 JSON 字符串
- qqmusic_data: str - QQ 音乐数据 JSON 字符串

输出变量:
- normalized_data: dict - 规范化后的数据对象
"""

import json
import re


def normalize_string(s: str) -> str:
    """规范化字符串"""
    if not s:
        return ""
    # 转小写
    s = s.lower()
    # 去除首尾空白
    s = s.strip()
    # 去除多余空格
    s = re.sub(r'\s+', ' ', s)
    return s


def normalize_artists(artists) -> list:
    """
    规范化歌手列表
    处理各种格式：字符串、列表、用分隔符分隔的字符串
    """
    if not artists:
        return []
    
    # 如果已经是列表
    if isinstance(artists, list):
        result = []
        for artist in artists:
            if isinstance(artist, str):
                result.append(normalize_string(artist))
            elif isinstance(artist, dict):
                result.append(normalize_string(artist.get('name', '')))
        return sorted(result)
    
    # 如果是字符串，尝试分割
    if isinstance(artists, str):
        # 尝试多种分隔符
        for separator in ['/', ',', '、', ';']:
            if separator in artists:
                return sorted([normalize_string(a) for a in artists.split(separator)])
        # 没有分隔符，作为单个歌手
        return [normalize_string(artists)]
    
    return []


def normalize_credits(credits: dict) -> dict:
    """
    规范化制作人员信息
    统一不同平台的字段名称
    """
    if not credits or not isinstance(credits, dict):
        return {}
    
    # 字段映射：将不同平台的字段名映射到标准名称
    field_mapping = {
        # 作词
        'lyricist': ['lyricist', 'lyrics', 'writer', 'written by', '作词', '词'],
        # 作曲
        'composer': ['composer', 'composition', 'music', 'composed by', '作曲', '曲'],
        # 编曲
        'arranger': ['arranger', 'arrangement', 'arranged by', '编曲'],
        # 制作人
        'producer': ['producer', 'produced by', '制作人', '监制'],
        # 混音
        'mixer': ['mixer', 'mixing', 'mixed by', '混音'],
        # 母带
        'mastering': ['mastering', 'mastered by', '母带', '母带工程师']
    }
    
    normalized = {}
    
    for standard_key, variants in field_mapping.items():
        for key, value in credits.items():
            normalized_key = normalize_string(key)
            if normalized_key in [normalize_string(v) for v in variants]:
                # 规范化人名列表
                if isinstance(value, list):
                    normalized[standard_key] = sorted([normalize_string(v) for v in value])
                elif isinstance(value, str):
                    # 分割可能的多个人名
                    names = [normalize_string(n) for n in re.split(r'[,/、;]', value)]
                    normalized[standard_key] = sorted(names)
                break
    
    return normalized


def parse_spotify_data(data_str: str) -> dict:
    """解析 Spotify 数据"""
    try:
        data = json.loads(data_str) if isinstance(data_str, str) else data_str
        
        # 提取歌手
        artists = normalize_artists([a.get('name') for a in data.get('artists', [])])
        
        # 提取专辑信息
        album = data.get('album', {})
        
        # Spotify 的制作人员信息在 external_ids 或需要额外 API 调用
        # 这里简化处理
        
        return {
            'title': normalize_string(data.get('name', '')),
            'artists': artists,
            'album': normalize_string(album.get('name', '')),
            'cover_url': album.get('images', [{}])[0].get('url', '') if album.get('images') else '',
            'duration_ms': data.get('duration_ms', 0),
            'credits': {}  # Spotify 需要额外 API 获取制作人员信息
        }
    except Exception as e:
        return {'error': f'Spotify 数据解析失败: {str(e)}'}


def parse_qqmusic_data(data_str: str) -> dict:
    """解析 QQ 音乐数据"""
    try:
        data = json.loads(data_str) if isinstance(data_str, str) else data_str
        
        # QQ 音乐 API 结构可能不同，需要根据实际调整
        song_data = data.get('data', {})
        
        # 提取歌手
        singers = song_data.get('singer', [])
        artists = normalize_artists([s.get('name') for s in singers] if isinstance(singers, list) else [])
        
        return {
            'title': normalize_string(song_data.get('songname', '')),
            'artists': artists,
            'album': normalize_string(song_data.get('albumname', '')),
            'cover_url': song_data.get('albummid', ''),  # 需要构造完整 URL
            'duration_ms': song_data.get('interval', 0) * 1000,
            'credits': {}  # QQ 音乐可能不提供详细制作人员信息
        }
    except Exception as e:
        return {'error': f'QQ 音乐数据解析失败: {str(e)}'}


def main(netease_data: dict, spotify_data: str, qqmusic_data: str) -> dict:
    """
    规范化来自不同平台的元数据
    """
    try:
        # 规范化网易云数据
        netease_normalized = {
            'title': normalize_string(netease_data.get('song_title', '')),
            'artists': normalize_artists(netease_data.get('artists', [])),
            'album': normalize_string(netease_data.get('album_name', '')),
            'cover_url': netease_data.get('cover_art_url', ''),
            'duration_ms': netease_data.get('duration_ms', 0),
            'credits': normalize_credits(netease_data.get('credits', {})),
            'lyrics': netease_data.get('lyrics', {})
        }
        
        # 解析并规范化 Spotify 数据
        spotify_normalized = parse_spotify_data(spotify_data) if spotify_data else {}
        
        # 解析并规范化 QQ 音乐数据
        qqmusic_normalized = parse_qqmusic_data(qqmusic_data) if qqmusic_data else {}
        
        return {
            'normalized_data': {
                'netease': netease_normalized,
                'spotify': spotify_normalized,
                'qqmusic': qqmusic_normalized
            },
            'success': True,
            'error': None
        }
    
    except Exception as e:
        return {
            'normalized_data': None,
            'success': False,
            'error': f'数据规范化失败: {str(e)}'
        }
