"""
解析封面图 URL 节点
解析 HTTP 响应并提取封面图 URL

输入变量:
- cover_response: str - QQ Music 封面图 API 响应

输出变量:
- cover_url: str - 封面图 URL
- success: bool - 解析状态
- error: str - 错误信息
"""

import json
from models import ParseCoverUrlOutput


def main(qqmusic_cover_response) -> ParseCoverUrlOutput:
    """
    解析 QQ 音乐封面图 API 响应
    处理 Dify HTTP 节点的字符串包装
    """
    try:
        # 1. 处理 Dify HTTP 节点包装
        if isinstance(qqmusic_cover_response, str):
            cover_data = json.loads(qqmusic_cover_response)
        else:
            cover_data = qqmusic_cover_response

        # 2. 提取 imageUrl
        image_url = cover_data.get("imageUrl", "")

        output = ParseCoverUrlOutput(cover_url=image_url, success=True, error="")
        return output

    except Exception as e:
        output = ParseCoverUrlOutput(cover_url="", success=False, error=str(e))
        return output
