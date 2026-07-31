import sys; sys.path.insert(0,'.')
from app.services.agent import _get_deepseek_client

c = _get_deepseek_client()
# Test with minimal tools
tools = [{
    "type": "function",
    "function": {
        "name": "search_product_kb",
        "description": "Search telecom product database",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
}]
try:
    r = c.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Search for youth plans"}],
        tools=tools,
        tool_choice="auto",
        max_tokens=100,
        timeout=15
    )
    msg = r.choices[0].message
    print("Has tool_calls:", bool(msg.tool_calls))
    print("Content:", msg.content)
except Exception as e:
    print("ERROR:", e)