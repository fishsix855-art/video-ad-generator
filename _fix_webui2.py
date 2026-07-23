with open("webui/Main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Better error display
old = 'st.error("生成失败: " + task.get("message", "未知错误"))'
new = 'st.error("生成失败: " + str(task.get("message") or task.get("error") or "未知错误")[:200])'
content = content.replace(old, new)

# Fix 2: Pass duration
old2 = '"video_concat_mode": "random",'
new2 = '"video_concat_mode": "random", "video_clip_duration": st.session_state.get("quick_mode_duration", 8),'
content = content.replace(old2, new2)

with open("webui/Main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed")
