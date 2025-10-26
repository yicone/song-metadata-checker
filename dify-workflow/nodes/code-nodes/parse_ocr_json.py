"""
OCR JSON 解析节点
解析 Gemini API 返回的 OCR 结果并合并到元数据

输入变量:
- gemini_response: str - Gemini API 响应 JSON 字符串
- metadata: dict - 当前元数据对象

输出变量:
- metadata: dict - 更新后的元数据对象（包含制作人员信息）
"""

import json
import re


def extract_json_from_text(text: str) -> dict:
    """
    从文本中提取 JSON 对象
    处理 LLM 可能返回的各种格式
    """
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试提取 JSON 代码块
    json_pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    if matches:
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError:
            pass
    
    # 尝试提取任何 JSON 对象
    json_pattern = r'\{.*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    return None


def main(gemini_response: str, metadata: dict) -> dict:
    """
    解析 Gemini OCR 响应并合并制作人员信息到元数据
    """
    try:
        # 解析 Gemini API 响应
        response_data = json.loads(gemini_response)
        
        # 提取生成的文本
        candidates = response_data.get('candidates', [])
        if not candidates:
            return {
                'metadata': metadata,
                'success': False,
                'error': 'Gemini 响应中未找到候选结果'
            }
        
        content = candidates[0].get('content', {})
        parts = content.get('parts', [])
        if not parts:
            return {
                'metadata': metadata,
                'success': False,
                'error': 'Gemini 响应中未找到文本内容'
            }
        
        text = parts[0].get('text', '')
        
        # 从文本中提取 JSON
        credits_data = extract_json_from_text(text)
        
        if credits_data is None:
            return {
                'metadata': metadata,
                'success': False,
                'error': 'OCR 结果不是有效的 JSON 格式'
            }
        
        # 合并制作人员信息到元数据
        if isinstance(metadata, dict):
            metadata['credits'] = credits_data
            
            return {
                'metadata': metadata,
                'success': True,
                'error': None
            }
        else:
            return {
                'metadata': metadata,
                'success': False,
                'error': '元数据格式无效'
            }
    
    except json.JSONDecodeError as e:
        return {
            'metadata': metadata,
            'success': False,
            'error': f'JSON 解析失败: {str(e)}'
        }
    except Exception as e:
        return {
            'metadata': metadata,
            'success': False,
            'error': f'OCR 解析失败: {str(e)}'
        }
