#!/usr/bin/env python3
"""
QQ 音乐 API 代理服务器（转发到 Rain120/qq-music-api）
将请求转发到实际的 QQ 音乐 API 服务
"""

import os
import sys
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PORT = int(os.getenv("PORT", 3001))
# Rain120/qq-music-api 的实际地址
QQMUSIC_API_BASE = os.getenv("QQMUSIC_API_BASE", "http://localhost:3200")


@app.route("/")
def index():
    """健康检查端点"""
    return jsonify(
        {
            "status": "ok",
            "service": "QQ Music API Proxy",
            "version": "1.0.0",
            "upstream": QQMUSIC_API_BASE,
        }
    )


@app.route("/search")
def search():
    """
    搜索歌曲（代理到 Rain120 API）
    参数:
        key: 搜索关键词
        pageSize: 每页数量 (默认 10)
        pageNo: 页码 (默认 1)
    """
    try:
        keyword = request.args.get("key", "")
        page_size = int(request.args.get("pageSize", 10))
        page_no = int(request.args.get("pageNo", 1))

        if not keyword:
            return jsonify({"error": "缺少搜索关键词"}), 400

        # 转发到 Rain120 API
        # Rain120 使用 /getSearchByKey 端点
        url = f"{QQMUSIC_API_BASE}/getSearchByKey"
        params = {"key": keyword, "pageSize": page_size, "pageNo": page_no}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # 日志输出到 stderr（Docker 容器可见）
        print(
            f"[QQ Music API] Search Response: {response.json()}",
            file=sys.stderr,
            flush=True,
        )

        # 使用 jsonify 返回，Dify 会自动包装
        return jsonify(response.json()["response"]["data"])

    except requests.RequestException as e:
        return jsonify(
            {"error": f"上游 API 调用失败: {str(e)}", "upstream": QQMUSIC_API_BASE}
        ), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/song")
def get_song():
    """
    获取歌曲详情
    参数:
        songmid: 歌曲 MID
    """
    try:
        songmid = request.args.get("songmid", "")

        if not songmid:
            return jsonify({"error": "缺少歌曲 MID"}), 400

        # 转发到 Rain120 API
        # Rain120 使用 /getSongInfo 端点
        url = f"{QQMUSIC_API_BASE}/getSongInfo"
        params = {"songmid": songmid}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # 日志输出到 stderr（Docker 容器可见）
        print(
            f"[QQ Music API] Response: {response.json()}", file=sys.stderr, flush=True
        )

        # 使用 jsonify 返回，Dify 会自动包装
        return jsonify(response.json()["response"]["songinfo"]["data"])

    except requests.RequestException as e:
        return jsonify(
            {"error": f"上游 API 调用失败: {str(e)}", "upstream": QQMUSIC_API_BASE}
        ), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print(f"QQ Music API Proxy starting on port {PORT}...")
    print(f"Forwarding to: {QQMUSIC_API_BASE}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
