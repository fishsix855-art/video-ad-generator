"""
Agent 模块 - 简单的 while-loop Agent with Function Calling
不依赖 LangChain，纯手写，面试能逐行讲清楚
"""
import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

MAX_STEPS = 10
TIMEOUT = 30
# Tools that should pause the agent for user input
INTERRUPT_TOOLS = {"generate_creative_ideas"}

# State persistence
def save_agent_state(session_id: str, state: dict):
    """Save agent state to database for later resume."""
    try:
        from app.services import database
        import json as _json
        database.save_task({
            "id": session_id,
            "user_input": state.get("user_message", ""),
            "style": state.get("style", ""),
            "duration": state.get("duration", 8),
            "prompt": "",
            "final_prompt": "",
            "status": "waiting_user",
            "task_data": _json.dumps({
                "agent_state": {
                    "messages": state.get("messages", []),
                    "step": state.get("step", 0),
                    "tools": state.get("tools", []),
                    "tool_handlers": list(state.get("tool_handlers", {}).keys()),
                }
            }, ensure_ascii=False),
        })
        return True
    except Exception:
        return False


def load_agent_state(session_id: str) -> dict | None:
    """Load agent state from database for resume."""
    try:
        from app.services import database
        import json as _json
        task = database.get_task(session_id)
        if not task:
            return None
        td = task.get("task_data", {})
        if isinstance(td, str):
            td = _json.loads(td)
        agent_state = td.get("agent_state", {})
        return agent_state if agent_state.get("messages") else None
    except Exception:
        return None




def _get_deepseek_client():
    """获取 DeepSeek API 客户端（从 config.toml 或环境变量读取）"""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        try:
            from app.config import config
            api_key = config.app.get("deepseek_api_key", "")
        except Exception:
            pass
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set in config.toml or environment")
    base_url = "https://api.deepseek.com/v1"
    try:
        from app.config import config
        custom_url = config.app.get("deepseek_base_url", "")
        if custom_url:
            base_url = custom_url
    except Exception:
        pass
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=TIMEOUT,
    )


def run_agent(
    system_prompt: str,
    user_message: str,
    tools: list[dict],
    tool_handlers: dict,
    max_steps: int = None,
    stream_callback: callable = None,
    session_id: str = "",
    resume_from: dict = None,
) -> dict:
    """
    运行 Agent 循环。
    
    Args:
        system_prompt: 系统提示词
        user_message: 用户输入
        tools: Function calling 工具定义列表
        tool_handlers: 工具名 → 函数的映射
        max_steps: 最大推理步数（默认 MAX_STEPS）
    
    Returns:
        {"answer": str, "steps": list[dict], "success": bool}
    """
    if max_steps is None:
        max_steps = MAX_STEPS
    
    client = _get_deepseek_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    steps = []
    
    # Resume from saved state if provided
    start_step = 1
    if resume_from and resume_from.get("messages"):
        messages = resume_from["messages"]
        start_step = resume_from.get("step", 1)
        logger.info(f"Resuming agent from step {start_step}")
    
    for step_num in range(start_step, max_steps + 1):
        step_record = {"step": step_num, "tool": None, "input": None, "result": None}
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=4096,
            )
        except Exception as e:
            logger.error(f"Agent step {step_num} failed: {e}")
            step_record["tool"] = "error"
            step_record["result"] = str(e)
            steps.append(step_record)
            return {"answer": f"Agent error at step {step_num}: {e}", "steps": steps, "success": False}
        
        msg = response.choices[0].message
        
        # No tool calls → final answer
        if not msg.tool_calls and msg.content:
            steps.append(step_record)
            return {"answer": msg.content, "steps": steps, "success": True}
        
        # No tool calls and no content → shouldn't happen, but handle gracefully
        if not msg.tool_calls:
            steps.append(step_record)
            return {"answer": "Agent stopped without a final answer.", "steps": steps, "success": False}
        
        # Process each tool call
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
            }
            for tc in msg.tool_calls
        ]})
        
        for tc in msg.tool_calls:
            tool_name = tc.function.name
            step_record["tool"] = tool_name
            step_record["input"] = tc.function.arguments[:300]
            
            # Notify stream callback
            if stream_callback:
                stream_callback({"type": "tool_start", "tool": tool_name, "step": step_num})
            
            handler = tool_handlers.get(tool_name)
            if not handler:
                tool_result = {"success": False, "error": f"Unknown tool: {tool_name}"}
            else:
                try:
                    args = json.loads(tc.function.arguments)
                    tool_result = handler(**args)
                except json.JSONDecodeError:
                    tool_result = {"success": False, "error": "Invalid JSON arguments"}
                except Exception as e:
                    tool_result = {"success": False, "error": str(e)}
            
            step_record["result"] = json.dumps(tool_result, ensure_ascii=False)[:500]
            
            # Check if this tool requires user interaction (interrupt)
            if tool_name in INTERRUPT_TOOLS and tool_result.get("status") == "needs_user_choice":
                if session_id:
                    save_agent_state(session_id, {
                        "messages": messages,
                        "step": step_num,
                        "tools": tools,
                        "tool_handlers": tool_handlers,
                        "user_message": user_message,
                    })
                return {
                    "answer": tool_result.get("message", "Agent paused"),
                    "steps": steps,
                    "success": True,
                    "status": "waiting_user",
                    "options": tool_result.get("options", []),
                    "session_id": session_id,
                }
            
            # Notify stream callback
            if stream_callback:
                stream_callback({"type": "tool_done", "tool": tool_name, "step": step_num, "result": str(tool_result)[:200]})
            
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(tool_result, ensure_ascii=False),
            })
        
        steps.append(step_record)
    
    # Max steps reached, ask for final answer
    messages.append({"role": "user", "content": "请根据以上分析，直接给出最终结果。"})
    try:
        final_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )
        return {"answer": final_response.choices[0].message.content, "steps": steps, "success": True}
    except Exception as e:
        return {"answer": f"Agent exhausted max steps ({max_steps}). Error: {e}", "steps": steps, "success": False}