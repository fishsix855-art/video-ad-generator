# Read the file
with open("webui/quick_app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the line with generate_creative_ideas (around line 191)
target_line = None
for i, line in enumerate(lines):
    if "ideas = llm.generate_creative_ideas(quick_input)" in line and "st.session_state.quick_mode_ideas" not in line:
        target_line = i
        break

if target_line is None:
    print("Could not find target line")
else:
    print(f"Found at line {target_line+1}: {lines[target_line].strip()[:80]}")

    # Replace with RAG-enhanced version
    indent = "                    "
    rag_block = [
        indent + "agent_on = _features.get(\"agent_enabled\", False)\n",
        indent + "if agent_on:\n",
        indent + "    try:\n",
        indent + "        from app.services import rag\n",
        indent + "        rag_result = rag.search_product_kb(quick_input)\n",
        indent + "        rag_data = rag_result.get(\"data\", [])\n",
        indent + "        rag_context = \"\"\n",
        indent + "        steps = []\n",
        indent + "        if rag_data:\n",
        indent + "            for rd in rag_data:\n",
        indent + "                rag_context += rd[\"content\"][:200] + \"\\n\"\n",
        indent + "            steps.append({\"step\": 1, \"tool\": \"search_product_kb\", \"result\": \"Found \" + str(len(rag_data)) + \" products\"})\n",
        indent + "        enhanced = quick_input\n",
        indent + "        if rag_context:\n",
        indent + "            enhanced = quick_input + \"。参考产品：\" + rag_context[:500]\n",
        indent + "        ideas = llm.generate_creative_ideas(enhanced)\n",
        indent + "        steps.append({\"step\": 2, \"tool\": \"generate_ideas\", \"result\": \"Generated \" + str(len(ideas)) + \" ideas\"})\n",
        indent + "        st.session_state.quick_mode_ideas = ideas\n",
        indent + "        st.session_state.quick_mode_agent_steps = steps\n",
        indent + "        st.session_state.quick_mode_step = \"choose\"\n",
        indent + "        st.session_state.quick_mode_selected = -1\n",
        indent + "        st.rerun()\n",
        indent + "    except Exception:\n",
        indent + "        st.warning(\"RAG mode failed, falling back to normal...\")\n",
        indent + "        st.session_state.pop(\"quick_mode_agent_steps\", None)\n",
    ]
    
    # Remove the old line (it will be replaced by the last line of rag_block which falls through)
    # Actually, we need to insert before and replace the old line
    # The old line is: "                    ideas = llm.generate_creative_ideas(quick_input)\n"
    # This line needs to be kept as fallback (when agent_on is False or exception)
    # So the flow is: [rag_block] + [old line as fallback]
    
    # Insert rag_block and keep the old line
    new_lines = lines[:target_line] + rag_block + lines[target_line:]
    
    # Now add agent steps display in the choose step
    # Find "elif st.session_state.quick_mode_step == \"choose\":""
    choose_line = None
    for i, line in enumerate(new_lines):
        if 'elif st.session_state.quick_mode_step == "choose":' in line:
            choose_line = i
            break
    
    if choose_line:
        # Add agent steps display after the choose header
        steps_display = [
            "    # Show Agent RAG steps if available\n",
            "    agent_steps = st.session_state.get(\"quick_mode_agent_steps\", [])\n",
            "    if agent_steps:\n",
            "        with st.expander(\"RAG (\" + str(len(agent_steps)) + \" steps)\", expanded=False):\n",
            "            for s in agent_steps:\n",
            "                st.caption(\"Step \" + str(s[\"step\"]) + \": \" + s.get(\"tool\", \"\"))\n",
            "                if s.get(\"result\"):\n",
            "                    st.text(str(s[\"result\"])[:300])\n",
        ]
        # Insert after the choose line + 1
        insert_pos = choose_line + 1
        for j, dl in enumerate(steps_display):
            new_lines.insert(insert_pos + j, dl)
        print(f"Added agent steps display after line {choose_line+1}")
    
    with open("webui/quick_app.py", "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Total lines: {len(new_lines)}")