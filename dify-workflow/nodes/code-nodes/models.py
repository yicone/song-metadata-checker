"""
TypedDict 类型定义
为所有 Code Node 的输出提供类型提示
使用 Python 标准库，无需第三方依赖
"""

from typing import TypedDict, Optional, List, Dict, Any


class ParseUrlOutput(TypedDict):
    """URL 解析输出"""

    song_id: Optional[str]
    success: bool
    error: str


class InitialDataStructuringOutput(TypedDict):
    """初始数据结构化输出"""

    metadata: Optional[Dict[str, Any]]
    success: bool
    error: str


class FindQQMusicMatchOutput(TypedDict):
    """QQ 音乐匹配输出"""

    match_id: str
    match_name: str
    match_album: str
    match_found: bool
    success: bool
    error: str


class ParseQQMusicResponseOutput(TypedDict):
    """QQ 音乐响应解析输出"""

    parsed_data: Dict[str, Any]
    track_name: str
    track_title: str
    album_id: int
    album_mid: str
    album_name: str
    album_pmid: str
    interval: int
    success: bool
    error: str


class ParseCoverUrlOutput(TypedDict):
    """封面图 URL 解析输出"""

    cover_url: str
    success: bool
    error: str


class DownloadAndEncodeCoversOutput(TypedDict):
    """下载并编码封面图输出"""

    netease_cover_base64: str
    qqmusic_cover_base64: str
    success: bool
    error: str


class ParseGeminiResponseOutput(TypedDict):
    """Gemini 响应解析输出"""

    is_same: bool
    confidence: float
    differences: List[str]
    notes: str
    raw_json: str
    success: bool
    error: str


class ConsolidateOutput(TypedDict):
    """数据整合与核验输出"""

    final_report: Dict[str, Any]
    success: bool
    error: str
