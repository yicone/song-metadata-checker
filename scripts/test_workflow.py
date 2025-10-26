#!/usr/bin/env python3
"""
工作流测试脚本
测试完整的音乐元数据核验工作流
"""

import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_workflow(song_url: str, credits_image_url: str = None):
    """
    测试工作流
    
    Args:
        song_url: 网易云音乐歌曲 URL
        credits_image_url: 制作人员图片 URL（可选）
    """
    print("=" * 60)
    print("工作流测试")
    print("=" * 60)
    print(f"歌曲 URL: {song_url}")
    if credits_image_url:
        print(f"制作人员图片: {credits_image_url}")
    print()
    
    # 检查是否配置了 Dify API
    dify_api_key = os.getenv('DIFY_API_KEY')
    dify_api_base = os.getenv('DIFY_API_BASE_URL')
    
    if not dify_api_key or not dify_api_base:
        print("⚠️  未配置 Dify API，将进行本地模拟测试")
        simulate_workflow(song_url, credits_image_url)
        return
    
    # 调用 Dify API
    print("📡 调用 Dify 工作流 API...")
    
    try:
        url = f"{dify_api_base}/workflows/run"
        headers = {
            'Authorization': f'Bearer {dify_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'inputs': {
                'song_url': song_url,
                'credits_image_url': credits_image_url or ''
            },
            'response_mode': 'blocking',
            'user': 'test-user'
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 工作流执行成功！")
            print("\n" + "=" * 60)
            print("核验报告")
            print("=" * 60)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ 工作流执行失败: {response.status_code}")
            print(f"响应: {response.text}")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 工作流测试失败: {str(e)}")
        sys.exit(1)


def simulate_workflow(song_url: str, credits_image_url: str = None):
    """
    本地模拟工作流（用于测试各个步骤）
    """
    print("🔧 开始本地模拟测试...\n")
    
    # 步骤 1: 解析 URL
    print("步骤 1: 解析 URL")
    from urllib.parse import urlparse, parse_qs
    
    try:
        if '#' in song_url:
            fragment_part = song_url.split('#')[-1]
            if fragment_part.startswith('/'):
                fragment_part = fragment_part[1:]
            parsed_url = urlparse(f"http://dummy.com/{fragment_part}")
        else:
            parsed_url = urlparse(song_url)
        
        query_params = parse_qs(parsed_url.query)
        song_id = query_params['id'][0]
        print(f"✅ 提取歌曲 ID: {song_id}\n")
    except Exception as e:
        print(f"❌ URL 解析失败: {str(e)}")
        sys.exit(1)
    
    # 步骤 2: 获取网易云数据
    print("步骤 2: 获取网易云音乐数据")
    netease_host = os.getenv('NETEASE_API_HOST', 'http://localhost:3000')
    
    try:
        # 获取歌曲详情
        response = requests.get(f"{netease_host}/song/detail?ids={song_id}", timeout=10)
        if response.status_code == 200:
            song_data = response.json()
            song = song_data['songs'][0]
            print(f"✅ 歌曲: {song['name']}")
            print(f"   歌手: {', '.join([a['name'] for a in song['ar']])}")
            print(f"   专辑: {song['al']['name']}")
        else:
            print(f"❌ 获取歌曲详情失败: {response.status_code}")
            sys.exit(1)
        
        # 获取歌词
        response = requests.get(f"{netease_host}/lyric?id={song_id}", timeout=10)
        if response.status_code == 200:
            print("✅ 歌词获取成功\n")
        else:
            print(f"⚠️  歌词获取失败: {response.status_code}\n")
    
    except Exception as e:
        print(f"❌ 网易云数据获取失败: {str(e)}")
        sys.exit(1)
    
    # 步骤 3: Spotify 搜索
    print("步骤 3: Spotify 搜索与核验")
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if client_id and client_secret:
        try:
            import base64
            
            # OAuth 认证
            auth_str = f"{client_id}:{client_secret}"
            auth_base64 = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
            
            auth_response = requests.post(
                'https://accounts.spotify.com/api/token',
                headers={
                    'Authorization': f'Basic {auth_base64}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={'grant_type': 'client_credentials'},
                timeout=10
            )
            
            if auth_response.status_code == 200:
                access_token = auth_response.json()['access_token']
                
                # 搜索歌曲
                search_query = f"track:{song['name']} artist:{song['ar'][0]['name']}"
                search_response = requests.get(
                    f"https://api.spotify.com/v1/search?q={search_query}&type=track&limit=5",
                    headers={'Authorization': f'Bearer {access_token}'},
                    timeout=10
                )
                
                if search_response.status_code == 200:
                    tracks = search_response.json()['tracks']['items']
                    if tracks:
                        print(f"✅ 在 Spotify 找到 {len(tracks)} 个匹配结果")
                        print(f"   最佳匹配: {tracks[0]['name']} - {tracks[0]['artists'][0]['name']}\n")
                    else:
                        print("⚠️  Spotify 未找到匹配结果\n")
                else:
                    print(f"⚠️  Spotify 搜索失败: {search_response.status_code}\n")
            else:
                print(f"⚠️  Spotify 认证失败: {auth_response.status_code}\n")
        
        except Exception as e:
            print(f"⚠️  Spotify 测试失败: {str(e)}\n")
    else:
        print("⚠️  未配置 Spotify 凭证，跳过 Spotify 核验\n")
    
    print("=" * 60)
    print("✅ 本地模拟测试完成！")
    print("=" * 60)
    print("\n提示: 要测试完整工作流，请配置 Dify API 并导入工作流定义")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='测试音乐元数据核验工作流')
    parser.add_argument('--url', required=True, help='网易云音乐歌曲 URL')
    parser.add_argument('--credits-image', help='制作人员图片 URL（可选）')
    
    args = parser.parse_args()
    
    test_workflow(args.url, args.credits_image)


if __name__ == '__main__':
    main()
