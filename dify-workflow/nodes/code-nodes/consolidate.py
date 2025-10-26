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


def compare_field(netease_value, spotify_value, qqmusic_value, field_type='string') -> dict:
    """
    比较单个字段的值
    返回核验状态和详细信息
    """
    result = {
        'value': netease_value,
        'status': '未查到',
        'sources': {}
    }
    
    # 如果网易云值为空
    if not netease_value:
        result['status'] = '未查到'
        return result
    
    # 字符串类型比较
    if field_type == 'string':
        spotify_match = False
        qqmusic_match = False
        
        if spotify_value:
            result['sources']['spotify'] = spotify_value
            ratio = similarity_ratio(str(netease_value), str(spotify_value))
            if ratio >= 0.95:  # 几乎完全匹配
                spotify_match = True
            elif ratio >= 0.8:  # 相似但有差异
                result['status'] = '存疑'
                result['note'] = f'与 Spotify 数据相似但有差异 (相似度: {ratio:.2%})'
        
        if qqmusic_value:
            result['sources']['qqmusic'] = qqmusic_value
            ratio = similarity_ratio(str(netease_value), str(qqmusic_value))
            if ratio >= 0.95:
                qqmusic_match = True
            elif ratio >= 0.8 and result['status'] != '存疑':
                result['status'] = '存疑'
                result['note'] = f'与 QQ 音乐数据相似但有差异 (相似度: {ratio:.2%})'
        
        # 如果至少一个源完全匹配
        if spotify_match or qqmusic_match:
            result['status'] = '确认'
            result['confirmed_by'] = []
            if spotify_match:
                result['confirmed_by'].append('Spotify')
            if qqmusic_match:
                result['confirmed_by'].append('QQ音乐')
        
        # 如果两个源都有数据但都不匹配
        elif spotify_value and qqmusic_value and result['status'] != '存疑':
            result['status'] = '存疑'
            result['note'] = '多个数据源结果不一致'
    
    # 列表类型比较（如歌手列表）
    elif field_type == 'list':
        if not isinstance(netease_value, list):
            netease_value = [netease_value]
        
        spotify_match = False
        qqmusic_match = False
        
        if spotify_value and isinstance(spotify_value, list):
            result['sources']['spotify'] = spotify_value
            # 检查是否有重叠
            overlap = set(netease_value) & set(spotify_value)
            if overlap == set(netease_value):  # 完全匹配
                spotify_match = True
            elif overlap:  # 部分匹配
                result['status'] = '存疑'
                result['note'] = f'与 Spotify 数据部分匹配 (匹配: {list(overlap)})'
        
        if qqmusic_value and isinstance(qqmusic_value, list):
            result['sources']['qqmusic'] = qqmusic_value
            overlap = set(netease_value) & set(qqmusic_value)
            if overlap == set(netease_value):
                qqmusic_match = True
            elif overlap and result['status'] != '存疑':
                result['status'] = '存疑'
                result['note'] = f'与 QQ 音乐数据部分匹配 (匹配: {list(overlap)})'
        
        if spotify_match or qqmusic_match:
            result['status'] = '确认'
            result['confirmed_by'] = []
            if spotify_match:
                result['confirmed_by'].append('Spotify')
            if qqmusic_match:
                result['confirmed_by'].append('QQ音乐')
    
    # 如果所有源都没有数据
    if not spotify_value and not qqmusic_value:
        result['status'] = '未查到'
        result['note'] = '所有核验源均未找到该字段'
    
    return result


def compare_credits(netease_credits: dict, spotify_credits: dict, qqmusic_credits: dict) -> dict:
    """
    比较制作人员信息
    """
    result = {}
    
    # 获取所有可能的字段
    all_fields = set(netease_credits.keys()) | set(spotify_credits.keys()) | set(qqmusic_credits.keys())
    
    for field in all_fields:
        netease_value = netease_credits.get(field)
        spotify_value = spotify_credits.get(field)
        qqmusic_value = qqmusic_credits.get(field)
        
        result[field] = compare_field(netease_value, spotify_value, qqmusic_value, 'list')
    
    return result


def main(normalized_data: dict, cover_match_result: str) -> dict:
    """
    整合多源数据并生成最终核验报告
    """
    try:
        netease = normalized_data.get('netease', {})
        spotify = normalized_data.get('spotify', {})
        qqmusic = normalized_data.get('qqmusic', {})
        
        # 构建最终报告
        report = {
            'metadata': {
                'song_id': netease.get('song_id', ''),
                'source': 'NetEase Cloud Music',
                'verification_timestamp': None  # 可以添加时间戳
            },
            'fields': {}
        }
        
        # 比较歌曲标题
        report['fields']['title'] = compare_field(
            netease.get('title'),
            spotify.get('title'),
            qqmusic.get('title'),
            'string'
        )
        
        # 比较歌手
        report['fields']['artists'] = compare_field(
            netease.get('artists'),
            spotify.get('artists'),
            qqmusic.get('artists'),
            'list'
        )
        
        # 比较专辑
        report['fields']['album'] = compare_field(
            netease.get('album'),
            spotify.get('album'),
            qqmusic.get('album'),
            'string'
        )
        
        # 封面图核验
        cover_status = '未查到'
        if cover_match_result:
            result_lower = cover_match_result.lower().strip()
            if '相同' in result_lower or 'same' in result_lower or 'yes' in result_lower:
                cover_status = '确认'
            elif '不相同' in result_lower or 'different' in result_lower or 'no' in result_lower:
                cover_status = '存疑'
        
        report['fields']['cover_art'] = {
            'value': netease.get('cover_url'),
            'status': cover_status,
            'sources': {
                'spotify': spotify.get('cover_url'),
                'qqmusic': qqmusic.get('cover_url')
            },
            'ai_comparison': cover_match_result
        }
        
        # 比较制作人员信息
        report['fields']['credits'] = compare_credits(
            netease.get('credits', {}),
            spotify.get('credits', {}),
            qqmusic.get('credits', {})
        )
        
        # 歌词（通常只有网易云有，作为事实来源）
        report['fields']['lyrics'] = {
            'value': netease.get('lyrics'),
            'status': '确认',
            'note': '来自源平台，无需核验'
        }
        
        # 生成摘要统计
        total_fields = 0
        confirmed_fields = 0
        questionable_fields = 0
        not_found_fields = 0
        
        def count_status(field_data):
            nonlocal total_fields, confirmed_fields, questionable_fields, not_found_fields
            if isinstance(field_data, dict):
                if 'status' in field_data:
                    total_fields += 1
                    status = field_data['status']
                    if status == '确认':
                        confirmed_fields += 1
                    elif status == '存疑':
                        questionable_fields += 1
                    elif status == '未查到':
                        not_found_fields += 1
                else:
                    # 递归处理嵌套字段（如 credits）
                    for value in field_data.values():
                        count_status(value)
        
        for field_data in report['fields'].values():
            count_status(field_data)
        
        report['summary'] = {
            'total_fields': total_fields,
            'confirmed': confirmed_fields,
            'questionable': questionable_fields,
            'not_found': not_found_fields,
            'confidence_score': confirmed_fields / total_fields if total_fields > 0 else 0
        }
        
        return {
            'final_report': report,
            'success': True,
            'error': None
        }
    
    except Exception as e:
        return {
            'final_report': None,
            'success': False,
            'error': f'数据整合失败: {str(e)}'
        }
