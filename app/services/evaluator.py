"""
Prompt 质量评测器 - Agent 生成提示词后自评
"""
import re
import json


def evaluate_prompt_quality(
    prompt: str,
    min_slices: int = 4,
    min_length: int = 300,
    required_keywords: list[str] = None,
) -> dict:
    """
    评测视频提示词质量。
    
    检查项：
    1. 时间切片标注（如 "0.0-1.0秒"）
    2. 时间切片数量是否达标
    3. 提示词总长度是否达标
    4. 画质约束关键词（竖屏、高清等）
    5. 自定义必须关键词
    
    Returns:
        {"passed": bool, "score": float, "issues": list[str], "details": dict}
    """
    if required_keywords is None:
        required_keywords = ["9:16", "高清", "画面稳定", "无肢体畸形"]
    
    issues = []
    details = {}
    
    # Check 1: time slices
    slices = re.findall(r"\d+\.?\d*-\d+\.?\d*秒", prompt)
    details["slices"] = slices
    details["slices_count"] = len(slices)
    if not slices:
        issues.append("缺少时间切片标注（如 0.0-1.0秒）")
    elif len(slices) < min_slices:
        issues.append(f"时间切片数量不足：需要至少 {min_slices} 个，当前 {len(slices)} 个")
    
    # Check 2: total length
    details["total_length"] = len(prompt)
    if len(prompt) < min_length:
        issues.append(f"提示词长度不足：需要至少 {min_length} 字，当前 {len(prompt)} 字")
    
    # Check 3: quality keywords
    missing_keywords = [kw for kw in required_keywords if kw not in prompt]
    details["missing_keywords"] = missing_keywords
    if missing_keywords:
        issues.append(f"缺少画质约束：{', '.join(missing_keywords)}")
    
    # Check 4: structure keywords
    structure_checks = {
        "场景描述": "场景总描述" in prompt or "场景描述" in prompt or "场景：" in prompt,
        "时间分段": "0." in prompt and "秒" in prompt,
        "画质约束": "9:16" in prompt or "竖屏" in prompt,
    }
    details["structure"] = structure_checks
    missing_structure = [k for k, v in structure_checks.items() if not v]
    if missing_structure:
        issues.append(f"缺少结构元素：{', '.join(missing_structure)}")
    
    passed = len(issues) == 0
    score = max(0.0, 1.0 - len(issues) * 0.2)
    
    return {
        "passed": passed,
        "score": round(score, 2),
        "issues": issues,
        "details": details,
    }


def evaluate_creative_ideas(ideas: list[dict]) -> dict:
    """
    评测创意方案质量。
    
    检查项：
    1. 数量是否达标（6个）
    2. 每个方案是否包含必要字段
    3. 风格是否不重复
    4. 描述长度是否合理
    """
    issues = []
    details = {}
    
    details["count"] = len(ideas)
    if len(ideas) < 3:
        issues.append(f"创意方案数量不足：需要至少 3 个，当前 {len(ideas)} 个")
    elif len(ideas) < 6:
        issues.append(f"创意方案数量偏少：期望 6 个，当前 {len(ideas)} 个")
    
    # Check field completeness
    required_fields = ["title", "description", "style"]
    for i, idea in enumerate(ideas):
        for field in required_fields:
            if field not in idea or not idea[field]:
                issues.append(f"方案 {i+1} 缺少字段：{field}")
    
    # Check style uniqueness
    styles = [idea.get("style", "") for idea in ideas]
    style_counts = {}
    for s in styles:
        style_counts[s] = style_counts.get(s, 0) + 1
    duplicates = [s for s, c in style_counts.items() if c > 1]
    details["style_duplicates"] = duplicates
    if duplicates:
        issues.append(f"风格重复：{', '.join(duplicates)}")
    
    # Check description length
    short_descriptions = 0
    for idea in ideas:
        desc = idea.get("description", "")
        if len(desc) < 20:
            short_descriptions += 1
    if short_descriptions > 0:
        issues.append(f"{short_descriptions} 个方案的描述过短（<20字）")
    
    passed = len(issues) == 0
    score = max(0.0, 1.0 - len(issues) * 0.15)
    
    return {
        "passed": passed,
        "score": round(score, 2),
        "issues": issues,
        "details": details,
    }


def format_evaluation_for_agent(eval_result: dict) -> str:
    """将评测结果格式化为 Agent 可读的反馈文本"""
    if eval_result["passed"]:
        return "✓ 质量评测通过，所有检查项均达标。"
    
    lines = [f"✗ 质量评测未通过 (得分: {eval_result['score']})"]
    for issue in eval_result["issues"]:
        lines.append(f"  - {issue}")
    return "\n".join(lines)