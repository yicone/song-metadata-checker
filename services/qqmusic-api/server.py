#!/usr/bin/env python3
"""
QQ 音乐 API 代理服务器
使用 qqmusic-api-python 库提供 RESTful API
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PORT = int(os.getenv('PORT', 3001))


@app.route('/')
def index():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'service': 'QQ Music API Proxy',
        'version': '1.0.0'
    })


@app.route('/search')
def search():
    """
    搜索歌曲
    参数:
        key: 搜索关键词
        pageSize: 每页数量 (默认 10)
        pageNo: 页码 (默认 1)
    """
    try:
        keyword = request.args.get('key', '')
        page_size = int(request.args.get('pageSize', 10))
        page_no = int(request.args.get('pageNo', 1))
        
        if not keyword:
            return jsonify({'error': '缺少搜索关键词'}), 400
        
        # TODO: 实际调用 QQ 音乐 API
        # 这里需要集成实际的 QQ 音乐 API 库
        # 例如：from qqmusic_api import search_song
        
        # 模拟返回数据结构
        result = {
            'code': 0,
            'data': {
                'song': {
                    'list': [
                        {
                            'songmid': 'example_mid_001',
                            'songname': '示例歌曲',
                            'singer': [
                                {'name': '示例歌手'}
                            ],
                            'albumname': '示例专辑',
                            'interval': 240
                        }
                    ],
                    'totalnum': 1
                }
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/song')
def get_song():
    """
    获取歌曲详情
    参数:
        songmid: 歌曲 MID
    """
    try:
        songmid = request.args.get('songmid', '')
        
        if not songmid:
            return jsonify({'error': '缺少歌曲 MID'}), 400
        
        # TODO: 实际调用 QQ 音乐 API
        # 模拟返回数据结构
        result = {
            'code': 0,
            'data': {
                'songmid': songmid,
                'songname': '示例歌曲',
                'singer': [
                    {'name': '示例歌手'}
                ],
                'albumname': '示例专辑',
                'albummid': 'example_album_mid',
                'interval': 240,
                'lyric': '示例歌词...'
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print(f'QQ Music API Proxy starting on port {PORT}...')
    app.run(host='0.0.0.0', port=PORT, debug=False)
