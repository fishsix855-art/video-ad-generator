path = "webui/quick_app.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Fix: check agent success before trying to parse
old_check = """                            answer = agent_result.get("answer","")
                            # Clean markdown code blocks"""

new_check = """                            answer = agent_result.get("answer","")
                            if not agent_result.get("success", False):
                                st.warning("Agent 推理失败: " + answer[:200])
                                raise ValueError("Agent failed: " + answer[:100])
                            # Clean markdown code blocks"""

code = code.replace(old_check, new_check)

# Also remove the debug write
code = code.replace('st.write("DEBUG answer:", answer[:500])\n                            # Extract JSON from answer', '# Extract JSON from answer')

with open(path, "w", encoding="utf-8") as f:
    f.write(code)
print("Fixed: check agent success first")