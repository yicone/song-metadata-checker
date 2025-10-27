"""
下载并转换封面图为 Base64 节点
下载两张封面图并转换为 base64 编码

输入变量:
- netease_cover_url: str - 网易云封面图 URL
- qqmusic_cover_url: str - QQ 音乐封面图 URL

输出变量:
- netease_cover_base64: str - 网易云封面图 base64
- qqmusic_cover_base64: str - QQ 音乐封面图 base64
- success: bool - 下载状态
- error: str - 错误信息
"""

import base64
import requests
from models import DownloadAndEncodeCoversOutput


def main(
    netease_cover_url: str, qqmusic_cover_url: str
) -> DownloadAndEncodeCoversOutput:
    """
    下载封面图并转换为 base64 编码
    Gemini Vision API 需要 base64 格式的图片数据
    """
    try:
        # 1. 下载网易云封面图
        netease_response = requests.get(netease_cover_url, timeout=10)
        netease_response.raise_for_status()
        netease_base64 = base64.b64encode(netease_response.content).decode("utf-8")

        # 2. 下载 QQ 音乐封面图
        qqmusic_response = requests.get(qqmusic_cover_url, timeout=10)
        qqmusic_response.raise_for_status()
        qqmusic_base64 = base64.b64encode(qqmusic_response.content).decode("utf-8")

        output = DownloadAndEncodeCoversOutput(
            netease_cover_base64=netease_base64,
            qqmusic_cover_base64=qqmusic_base64,
            success=True,
            error="",
        )
        return output

    except Exception as e:
        output = DownloadAndEncodeCoversOutput(
            netease_cover_base64="",
            qqmusic_cover_base64="",
            success=False,
            error=str(e),
        )
        return output
