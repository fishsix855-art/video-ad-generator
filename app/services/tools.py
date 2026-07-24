'''
Agent 工具集 - 供 Agent 的 LLM 通过 Function Calling 调用
每个函数返回 dict，包含 success 和 result/data 字段
'''
import json
from app.services import database


def search_relevant_cases(keywords: str, limit: int = 3) -> dict:
    '''
    搜索历史优秀创意案例。
    输入：关键词（如 "电信"、"套餐"、"优惠"）
    输出：匹配的历史案例列表
    '''
    try:
        cases = database.get_relevant_cases(keywords, limit)
        if not cases:
            return {"success": True, "data": [], "message": "未找到相关历史案例"}
        return {"success": True, "data": cases, "message": f"找到 {len(cases)} 个相关案例"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def save_creative_case(title: str, description: str, style: str = "", prompt: str = "", keywords: str = "", quality_score: float = 0.5) -> dict:
    '''
    保存一个创意方案到知识库。
    输入：标题、描述、风格、完整prompt、关键词、质量评分
    输出：保存结果
    '''
    try:
        database.save_creative_case({
            "title": title,
            "description": description,
            "style": style,
            "prompt": prompt,
            "keywords": keywords,
            "quality_score": quality_score,
        })
        return {"success": True, "message": f"案例 '{title}' 已保存"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def evaluate_prompt_quality(prompt: str, min_slices: int = 4, min_length: int = 300) -> dict:
    '''
    评测视频提示词质量。
    检查项：
    1. 是否包含时间切片（如 "0.0-1.0秒"）
    2. 时间切片数量是否达标
    3. 提示词总长度是否达标
    4. 是否包含画质约束（如 "9:16竖屏"、"高清"、"无肢体畸形"）
    输入：完整 prompt 文本、最少切片数、最短字数
    输出：通过/不通过 + 问题列表
    '''
    issues = []
    
    # Check 1: time slices
    import re
    slices = re.findall(r'\d+\.?\d*-\d+\.?\d*秒', prompt)
    if not slices:
        issues.append("缺少时间切片标注（如 0.0-1.0秒）")
    elif len(slices) < min_slices:
        issues.append(f"时间切片数量不足：需要至少 {min_slices} 个，当前 {len(slices)} 个")
    
    # Check 2: total length
    if len(prompt) < min_length:
        issues.append(f"提示词长度不足：需要至少 {min_length} 字，当前 {len(prompt)} 字")
    
    # Check 3: quality constraints
    quality_keywords = ["9:16", "竖屏", "高清", "画面稳定", "无肢体畸形"]
    missing = [kw for kw in quality_keywords if kw not in prompt]
    if missing:
        issues.append(f"缺少画质约束关键词：{', '.join(missing)}")
    
    passed = len(issues) == 0
    return {
        "success": True,
        "passed": passed,
        "issues": issues,
        "score": max(0, 1.0 - len(issues) * 0.25),
        "slices_count": len(slices),
        "total_length": len(prompt),
    }


# Function Calling 工具定义（给 LLM 看的 tool schema）
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_relevant_cases",
            "description": "搜索历史优秀创意案例。输入关键词如'电信优惠'、'新机发布'等，返回匹配的历史案例。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {"type": "string", "description": "搜索关键词"},
                    "limit": {"type": "integer", "description": "返回数量上限，默认3"}
                },
                "required": ["keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_creative_case",
            "description": "保存一个创意方案到知识库，供后续参考。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "方案标题"},
                    "description": {"type": "string", "description": "方案描述"},
                    "style": {"type": "string", "description": "视觉风格"},
                    "prompt": {"type": "string", "description": "完整视频提示词"},
                    "keywords": {"type": "string", "description": "关键词，用逗号分隔"},
                    "quality_score": {"type": "number", "description": "质量评分 0-1"}
                },
                "required": ["title", "description", "keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_prompt_quality",
            "description": "评测视频提示词质量，检查时间切片、长度、画质约束等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "要评测的提示词文本"},
                    "min_slices": {"type": "integer", "description": "最少时间切片数"},
                    "min_length": {"type": "integer", "description": "最少字数"}
                },
                "required": ["prompt"]
            }
        }
    }
]


# 工具函数映射表
TOOL_HANDLERS = {
    "search_relevant_cases": search_relevant_cases,
    "save_creative_case": save_creative_case,
    "evaluate_prompt_quality": evaluate_prompt_quality,
}
