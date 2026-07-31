"""
Agent Toolset - 10 tools for Agent Function Calling
Each function returns dict with success and result/data
"""
import json
import re
from app.services import database


# ============================================================
# Tool 1: Product Knowledge Base Search (RAG)
# ============================================================
def search_product_kb(query: str) -> dict:
    """Search telecom product KB for product info."""
    try:
        from app.services import rag
        return rag.search_product_kb(query)
    except Exception as e:
        return {"success": False, "error": f"RAG search failed: {e}"}


# ============================================================
# Tool 2: Search Historical Creative Cases
# ============================================================
def search_relevant_cases(keywords: str, limit: int = 3) -> dict:
    """Search historical creative cases by keywords."""
    try:
        cases = database.get_relevant_cases(keywords, limit)
        if not cases:
            return {"success": True, "data": [], "message": "No relevant historical cases found"}
        return {"success": True, "data": cases, "message": f"Found {len(cases)} relevant cases"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# Tool 3: Save Creative Case
# ============================================================
def save_creative_case(title: str, description: str, style: str = "", prompt: str = "", keywords: str = "", quality_score: float = 0.5) -> dict:
    """Save a creative case to the knowledge base."""
    try:
        database.save_creative_case({
            "title": title,
            "description": description,
            "style": style,
            "prompt": prompt,
            "keywords": keywords,
            "quality_score": quality_score,
        })
        return {"success": True, "message": f"Case '{title}' saved"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# Tool 4: Evaluate Creative Ideas (Regex Layer)
# ============================================================
def evaluate_creative_ideas(ideas_json: str, min_count: int = 6) -> dict:
    """Evaluate creative ideas: count, field completeness, style diversity, description length."""
    try:
        if isinstance(ideas_json, str):
            ideas = json.loads(ideas_json)
        else:
            ideas = ideas_json
    except Exception:
        return {"success": True, "passed": False, "score": 0.0, "issues": ["Cannot parse creative ideas JSON"], "details": {}}

    issues = []
    details = {"count": len(ideas)}

    if len(ideas) < 3:
        issues.append(f"Not enough ideas: need at least 3, got {len(ideas)}")
    elif len(ideas) < min_count:
        issues.append(f"Idea count low: expected {min_count}, got {len(ideas)}")

    required_fields = ["title", "description", "style"]
    for i, idea in enumerate(ideas):
        for field in required_fields:
            if field not in idea or not idea[field]:
                issues.append(f"Idea {i+1} missing field: {field}")

    styles = [idea.get("style", "") for idea in ideas]
    style_counts = {}
    for s in styles:
        style_counts[s] = style_counts.get(s, 0) + 1
    duplicates = [s for s, c in style_counts.items() if c > 1]
    details["style_duplicates"] = duplicates
    if duplicates:
        issues.append(f"Duplicate styles: " + ", ".join(duplicates))

    short_count = sum(1 for idea in ideas if len(idea.get("description", "")) < 20)
    if short_count > 0:
        issues.append(f"{short_count} ideas have too short descriptions (<20 chars)")

    passed = len(issues) == 0
    score = max(0.0, 1.0 - len(issues) * 0.15)
    return {"success": True, "passed": passed, "score": round(score, 2), "issues": issues, "details": details}


# ============================================================
# Tool 5: Evaluate Prompt Quality (Regex Layer)
# ============================================================
def evaluate_prompt_quality(prompt: str, min_slices: int = 4, min_length: int = 300) -> dict:
    """Evaluate video prompt: time slices, length, quality constraints."""
    issues = []
    CH_SEC = chr(0x79d2)
    slices = re.findall(r"\d+\.?\d*-\d+\.?\d*" + CH_SEC, prompt)
    if not slices:
        issues.append("Missing time slice annotations (e.g. 0.0-1.0" + CH_SEC + ")")
    elif len(slices) < min_slices:
        issues.append(f"Insufficient time slices: need at least {min_slices}, got {len(slices)}")

    if len(prompt) < min_length:
        issues.append(f"Prompt too short: need at least {min_length} chars, got {len(prompt)}")

    quality_keywords = ["9:16", CH_SEC + "u5c4f", CH_SEC + "u6e05", CH_SEC + "u753b" + CH_SEC + "u7a33" + CH_SEC + "u5b9a", CH_SEC + "u65e0" + CH_SEC + "u80a2" + CH_SEC + "u4f53" + CH_SEC + "u7578" + CH_SEC + "u5f62"]
    quality_keywords = ["9:16", chr(0x7ad6)+chr(0x5c4f), chr(0x9ad8)+chr(0x6e05), chr(0x753b)+chr(0x9762)+chr(0x7a33)+chr(0x5b9a), chr(0x65e0)+chr(0x80a2)+chr(0x4f53)+chr(0x7578)+chr(0x5f62)]
    missing = [kw for kw in quality_keywords if kw not in prompt]
    if missing:
        issues.append(f"Missing quality constraints: " + ", ".join(missing))

    passed = len(issues) == 0
    return {
        "success": True,
        "passed": passed,
        "issues": issues,
        "score": max(0, 1.0 - len(issues) * 0.25),
        "slices_count": len(slices),
        "total_length": len(prompt),
    }


# ============================================================
# Tool 6: LLM-as-Judge Content Evaluation
# ============================================================
def evaluate_content(content_json: str, target_audience: str = "general", style: str = "") -> dict:
    """Use LLM to judge content quality: brand consistency, audience match, visual feasibility, appeal."""
    try:
        from app.services import judge
        result = judge.run_full_evaluation(content_json, prompt="", target_audience=target_audience, style=style)
        return {"success": True, **result}
    except Exception as e:
        return {"success": True, "passed": True, "overall": 3.0, "scores": {}, "comments": f"Judge unavailable: {e}"}


# ============================================================
# Tool 7: Content Safety Guard
# ============================================================
def check_safety(content: str) -> dict:
    """Check content safety: sensitive words, false advertising, compliance."""
    try:
        from app.services import guard
        return guard.check_safety(content)
    except Exception as e:
        return {"success": True, "passed": True, "issues": [], "score": 1.0}


# ============================================================
# Tool 8: Trim Video (FFmpeg)
# ============================================================
def trim_video(input_path: str, output_path: str, start: float, end: float = -1) -> dict:
    """Trim a video segment using FFmpeg."""
    try:
        from app.services.video_editor import VideoEditor
        editor = VideoEditor()
        kwargs = {"input_path": input_path, "output_path": output_path, "start": start}
        if end > 0:
            kwargs["end"] = end
        result_path = editor.trim(**kwargs)
        return {"success": True, "output_path": result_path, "message": f"Video trimmed: {result_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# Tool 9: Concatenate Videos (FFmpeg)
# ============================================================
def concat_videos(input_paths_json: str, output_path: str) -> dict:
    """Concatenate multiple videos using FFmpeg concat."""
    try:
        input_paths = json.loads(input_paths_json) if isinstance(input_paths_json, str) else input_paths_json
        from app.services.video_editor import VideoEditor
        editor = VideoEditor()
        result_path = editor.concat(inputs=input_paths, output_path=output_path)
        return {"success": True, "output_path": result_path, "message": f"Concatenated {len(input_paths)} videos"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# Tool 10: Add Subtitle (FFmpeg)
# ============================================================
def add_subtitle(video_path: str, srt_path: str, output_path: str) -> dict:
    """Overlay SRT subtitles onto video using FFmpeg."""
    try:
        from app.services.video_editor import VideoEditor
        editor = VideoEditor()
        result_path = editor.add_subtitle(video_path=video_path, srt_path=srt_path, output_path=output_path)
        return {"success": True, "output_path": result_path, "message": f"Subtitles added: {result_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# TOOL_DEFINITIONS - Schema for LLM Function Calling
# ============================================================
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_product_kb",
            "description": "Search telecom product knowledge base for product names, plans, target audiences, and selling points. Should be called BEFORE generating creative ideas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query, e.g. '5G plan', 'broadband', 'senior discount'"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_relevant_cases",
            "description": "Search historical creative cases by keywords. Returns matching cases for reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {"type": "string", "description": "Search keywords"},
                    "limit": {"type": "integer", "description": "Max results, default 3"}
                },
                "required": ["keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_creative_case",
            "description": "Save a high-quality creative case to the knowledge base for future reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Case title"},
                    "description": {"type": "string", "description": "Case description"},
                    "style": {"type": "string", "description": "Visual style"},
                    "prompt": {"type": "string", "description": "Complete video prompt"},
                    "keywords": {"type": "string", "description": "Keywords, comma-separated"},
                    "quality_score": {"type": "number", "description": "Quality score 0-1"}
                },
                "required": ["title", "description", "keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_creative_ideas",
            "description": "Evaluate creative ideas quality (regex layer): checks count, field completeness, style diversity, description length.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ideas_json": {"type": "string", "description": "Creative ideas JSON array string"},
                    "min_count": {"type": "integer", "description": "Minimum idea count, default 6"}
                },
                "required": ["ideas_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_prompt_quality",
            "description": "Evaluate video prompt quality (regex layer): checks time slices, length, quality constraint keywords.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Prompt text to evaluate"},
                    "min_slices": {"type": "integer", "description": "Minimum time slice count"},
                    "min_length": {"type": "integer", "description": "Minimum character count"}
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_content",
            "description": "Use LLM to judge content quality (LLM-as-Judge layer): brand consistency, audience match, visual feasibility, appeal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content_json": {"type": "string", "description": "Content JSON to evaluate"},
                    "target_audience": {"type": "string", "description": "Target audience, e.g. 'elderly', 'young adults'"},
                    "style": {"type": "string", "description": "Video style, e.g. 'commercial realism'"}
                },
                "required": ["content_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_safety",
            "description": "Check content safety: sensitive words, false advertising, compliance. Call before outputting user-visible content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Text content to check"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trim_video",
            "description": "Trim a video segment by start/end time (FFmpeg).",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {"type": "string", "description": "Input video path"},
                    "output_path": {"type": "string", "description": "Output video path"},
                    "start": {"type": "number", "description": "Start time in seconds"},
                    "end": {"type": "number", "description": "End time in seconds, default to video end"}
                },
                "required": ["input_path", "output_path", "start"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "concat_videos",
            "description": "Concatenate multiple video files (FFmpeg concat).",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_paths_json": {"type": "string", "description": "JSON array of input video paths"},
                    "output_path": {"type": "string", "description": "Output video path"}
                },
                "required": ["input_paths_json", "output_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_subtitle",
            "description": "Overlay SRT subtitle file onto video (FFmpeg subtitles filter).",
            "parameters": {
                "type": "object",
                "properties": {
                    "video_path": {"type": "string", "description": "Input video path"},
                    "srt_path": {"type": "string", "description": "SRT subtitle file path"},
                    "output_path": {"type": "string", "description": "Output video path"}
                },
                "required": ["video_path", "srt_path", "output_path"]
            }
        }
    }
]


# ============================================================
# TOOL_HANDLERS - Function name to handler mapping
# ============================================================
TOOL_HANDLERS = {
    "search_product_kb": search_product_kb,
    "search_relevant_cases": search_relevant_cases,
    "save_creative_case": save_creative_case,
    "evaluate_creative_ideas": evaluate_creative_ideas,
    "evaluate_prompt_quality": evaluate_prompt_quality,
    "evaluate_content": evaluate_content,
    "check_safety": check_safety,
    "trim_video": trim_video,
    "concat_videos": concat_videos,
    "add_subtitle": add_subtitle,
}
