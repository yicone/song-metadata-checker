"""
解析 Gemini 响应节点
解析 Gemini 返回的封面图比较结果

输入变量:
- gemini_response: str - Gemini Vision API 响应

输出变量:
- is_same: bool - 封面图是否相同
- confidence: float - 置信度 (0.0-1.0)
- differences: list - 差异列表
- notes: str - 额外说明
- raw_json: str - 原始 JSON 字符串
- success: bool - 解析状态
- error: str - 错误信息
"""

import json
import re
from models import ParseGeminiResponseOutput


def main(gemini_response) -> ParseGeminiResponseOutput:
    """
    解析 Gemini Vision API 响应
    提取封面图比较的 JSON 结果
    """
    try:
        # 1. 解析 HTTP 响应
        if isinstance(gemini_response, str):
            response_data = json.loads(gemini_response)
        else:
            response_data = gemini_response

        # 2. 提取 text 字段
        text = (
            response_data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        # 3. 提取 JSON（去除 markdown 代码块标记）
        # Gemini 可能返回: ```json\n{...}\n```
        json_match = re.search(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = text

        # 4. 解析 JSON
        comparison_result = json.loads(json_str)

        # 5. 提取关键字段
        is_same = comparison_result.get("is_same", False)
        confidence = comparison_result.get("confidence", 0.0)
        differences = comparison_result.get("differences", [])
        notes = comparison_result.get("notes", "")

        output = ParseGeminiResponseOutput(
            is_same=is_same,
            confidence=confidence,
            differences=differences,
            notes=notes,
            raw_json=json_str,
            success=True,
            error="",
        )
        return output

    except Exception as e:
        output = ParseGeminiResponseOutput(
            is_same=False,
            confidence=0.0,
            differences=[],
            notes="",
            raw_json="",
            success=False,
            error=str(e),
        )
        return output
