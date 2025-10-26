#!/usr/bin/env python3
"""
API 连通性测试脚本
测试所有外部 API 的可用性
"""

import os
import sys
import requests
import base64
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_netease_api():
    """测试网易云音乐 API"""
    print("🎵 测试网易云音乐 API...")
    host = os.getenv('NETEASE_API_HOST', 'http://localhost:3000')
    
    try:
        # 测试健康检查
        response = requests.get(f"{host}/", timeout=5)
        if response.status_code == 200:
            print("✅ 网易云音乐 API 连接成功")
            
            # 测试歌曲详情接口
            test_id = "2758218600"
            response = requests.get(f"{host}/song/detail?ids={test_id}", timeout=10)
            if response.status_code == 200:
                print(f"✅ 歌曲详情接口测试成功 (ID: {test_id})")
                return True
            else:
                print(f"❌ 歌曲详情接口测试失败: {response.status_code}")
                return False
        else:
            print(f"❌ 网易云音乐 API 连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 网易云音乐 API 测试失败: {str(e)}")
        return False


def test_qqmusic_api():
    """测试 QQ 音乐 API"""
    print("\n🎵 测试 QQ 音乐 API...")
    host = os.getenv('QQ_MUSIC_API_HOST', 'http://localhost:3001')
    
    try:
        # 测试健康检查
        response = requests.get(f"{host}/", timeout=5)
        if response.status_code == 200:
            print("✅ QQ 音乐 API 连接成功")
            
            # 测试搜索接口
            response = requests.get(f"{host}/search?key=周杰伦&pageSize=1", timeout=10)
            if response.status_code == 200:
                print("✅ QQ 音乐搜索接口测试成功")
                return True
            else:
                print(f"❌ QQ 音乐搜索接口测试失败: {response.status_code}")
                return False
        else:
            print(f"❌ QQ 音乐 API 连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ QQ 音乐 API 测试失败: {str(e)}")
        return False


def test_spotify_api():
    """测试 Spotify API（可选）"""
    print("\n🎧 测试 Spotify API（可选）...")
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    auth_url = os.getenv('SPOTIFY_AUTH_URL', 'https://accounts.spotify.com/api/token')
    
    if not client_id or not client_secret:
        print("⏭️  未配置 Spotify 凭证（已跳过）")
        return True  # 返回 True 因为这是可选的
    
    try:
        # 获取访问令牌
        auth_str = f"{client_id}:{client_secret}"
        auth_bytes = auth_str.encode('ascii')
        auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post(auth_url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            print("✅ Spotify OAuth 认证成功")
            
            # 测试搜索接口
            api_base = os.getenv('SPOTIFY_API_BASE_URL', 'https://api.spotify.com/v1')
            search_headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            search_response = requests.get(
                f"{api_base}/search?q=test&type=track&limit=1",
                headers=search_headers,
                timeout=10
            )
            
            if search_response.status_code == 200:
                print("✅ Spotify 搜索接口测试成功")
                return True
            else:
                print(f"❌ Spotify 搜索接口测试失败: {search_response.status_code}")
                return False
        else:
            print(f"❌ Spotify OAuth 认证失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Spotify API 测试失败: {str(e)}")
        return False


def test_gemini_api():
    """测试 Google Gemini API"""
    print("\n🤖 测试 Google Gemini API...")
    api_key = os.getenv('GEMINI_API_KEY')
    api_base = os.getenv('GEMINI_API_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta')
    
    if not api_key:
        print("❌ 未配置 Gemini API 密钥")
        return False
    
    try:
        url = f"{api_base}/models/gemini-2.5-flash:generateContent"
        headers = {
            'x-goog-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        data = {
            'contents': [{
                'parts': [{'text': 'Hello'}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            print("✅ Gemini API 测试成功")
            return True
        else:
            print(f"❌ Gemini API 测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Gemini API 测试失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("API 连通性测试")
    print("=" * 60)
    
    results = {
        '网易云音乐 API (数据源)': test_netease_api(),
        'QQ 音乐 API (核验源)': test_qqmusic_api(),
        'Gemini API (OCR)': test_gemini_api(),
        'Spotify API (可选)': test_spotify_api()
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for api_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{api_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有 API 测试通过！")
        sys.exit(0)
    else:
        print("⚠️  部分 API 测试失败，请检查配置")
        sys.exit(1)


if __name__ == '__main__':
    main()
