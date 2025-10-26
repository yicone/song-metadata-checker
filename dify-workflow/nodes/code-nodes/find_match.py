"""
匹配算法节点
从搜索结果中找到最佳匹配的歌曲

输入变量:
- search_results: str - 搜索结果 JSON 字符串
- target_title: str - 目标歌曲标题
- target_artists: list - 目标歌手列表
- platform: str - 平台名称 (spotify/qqmusic)

输出变量:
- match_id: str - 匹配的歌曲 ID
- match_found: bool - 是否找到匹配
"""

import json
from difflib import SequenceMatcher


def normalize_string(s: str) -> str:
    """规范化字符串用于比较"""
    return s.lower().strip()


def similarity_ratio(a: str, b: str) -> float:
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, normalize_string(a), normalize_string(b)).ratio()


def artists_match(artists1: list, artists2: list, threshold: float = 0.8) -> bool:
    """
    判断两个歌手列表是否匹配
    至少有一个歌手名称相似度超过阈值
    """
    for a1 in artists1:
        for a2 in artists2:
            if similarity_ratio(a1, a2) >= threshold:
                return True
    return False


def find_spotify_match(data: dict, target_title: str, target_artists: list) -> dict:
    """从 Spotify 搜索结果中找到最佳匹配"""
    tracks = data.get('tracks', {}).get('items', [])
    
    best_match = None
    best_score = 0.0
    
    for track in tracks:
        # 计算标题相似度
        title_similarity = similarity_ratio(track.get('name', ''), target_title)
        
        # 提取歌手名称
        artists = [artist.get('name', '') for artist in track.get('artists', [])]
        
        # 检查歌手匹配
        artist_match = artists_match(target_artists, artists)
        
        # 综合评分：标题相似度 * 0.7 + 歌手匹配 * 0.3
        score = title_similarity * 0.7 + (1.0 if artist_match else 0.0) * 0.3
        
        if score > best_score:
            best_score = score
            best_match = track
    
    # 如果最佳匹配的分数超过阈值（0.6），认为找到匹配
    if best_match and best_score >= 0.6:
        return {
            'match_id': best_match.get('id'),
            'match_found': True,
            'match_score': best_score,
            'match_name': best_match.get('name'),
            'match_artists': [a.get('name') for a in best_match.get('artists', [])]
        }
    
    return {
        'match_id': None,
        'match_found': False,
        'match_score': 0.0
    }


def find_qqmusic_match(data: dict, target_title: str, target_artists: list) -> dict:
    """从 QQ 音乐搜索结果中找到最佳匹配"""
    # QQ 音乐 API 的响应结构可能不同，需要根据实际 API 调整
    songs = data.get('data', {}).get('song', {}).get('list', [])
    
    best_match = None
    best_score = 0.0
    
    for song in songs:
        # 计算标题相似度
        title_similarity = similarity_ratio(song.get('songname', ''), target_title)
        
        # 提取歌手名称
        singers = song.get('singer', [])
        artists = [singer.get('name', '') for singer in singers] if isinstance(singers, list) else []
        
        # 检查歌手匹配
        artist_match = artists_match(target_artists, artists)
        
        # 综合评分
        score = title_similarity * 0.7 + (1.0 if artist_match else 0.0) * 0.3
        
        if score > best_score:
            best_score = score
            best_match = song
    
    # 如果最佳匹配的分数超过阈值（0.6），认为找到匹配
    if best_match and best_score >= 0.6:
        return {
            'match_id': best_match.get('songmid') or best_match.get('id'),
            'match_found': True,
            'match_score': best_score,
            'match_name': best_match.get('songname'),
            'match_artists': [s.get('name') for s in best_match.get('singer', [])]
        }
    
    return {
        'match_id': None,
        'match_found': False,
        'match_score': 0.0
    }


def main(search_results: str, target_title: str, target_artists: list, platform: str) -> dict:
    """
    从搜索结果中找到最佳匹配的歌曲
    """
    try:
        # 解析搜索结果
        data = json.loads(search_results)
        
        # 根据平台选择匹配算法
        if platform.lower() == 'spotify':
            result = find_spotify_match(data, target_title, target_artists)
        elif platform.lower() == 'qqmusic':
            result = find_qqmusic_match(data, target_title, target_artists)
        else:
            return {
                'match_id': None,
                'match_found': False,
                'error': f'不支持的平台: {platform}'
            }
        
        result['success'] = True
        result['error'] = None
        return result
    
    except json.JSONDecodeError as e:
        return {
            'match_id': None,
            'match_found': False,
            'success': False,
            'error': f'JSON 解析失败: {str(e)}'
        }
    except Exception as e:
        return {
            'match_id': None,
            'match_found': False,
            'success': False,
            'error': f'匹配失败: {str(e)}'
        }
