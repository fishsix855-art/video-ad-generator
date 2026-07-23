import re

with open("webui/Main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. In reference step: change transitions from prompt to duration
ref_start = content.find("# Step 4: Reference Image Upload")
ref_end = content.find("# Step 5: Edit Prompt")
ref_section = content[ref_start:ref_end]
ref_section = ref_section.replace("quick_mode_step = 'prompt'", "quick_mode_step = 'duration'")
content = content[:ref_start] + ref_section + content[ref_end:]

# 2. Insert duration step before Step 5
duration_step = '''
        # ============================================================
        # Step 4.5: Duration Selection
        # ============================================================
        elif st.session_state.quick_mode_step == "duration":
            if st.session_state.quick_mode_selected >= 0:
                idea = st.session_state.quick_mode_ideas[st.session_state.quick_mode_selected]
                st.info("方案: **{}** | 风格: **{}**".format(
                    idea.get("title", ""), st.session_state.quick_mode_style))

            st.markdown("### 选择视频时长")

            if "quick_mode_duration" not in st.session_state:
                st.session_state.quick_mode_duration = 8

            duration = st.slider(
                "视频时长（秒）",
                min_value=4,
                max_value=12,
                value=st.session_state.quick_mode_duration,
                step=1,
                help="Seedance v1.0 最大支持 12 秒",
            )
            st.session_state.quick_mode_duration = duration
            st.markdown("当前: **{} 秒**".format(duration))

            if st.session_state.quick_mode_selected >= 0:
                idea = st.session_state.quick_mode_ideas[st.session_state.quick_mode_selected]
                if not st.session_state.quick_mode_prompt:
                    has_ref = len(st.session_state.quick_mode_refs) > 0
                    ref_desc = ""
                    if has_ref:
                        names = [r["name"] for r in st.session_state.quick_mode_refs if r["name"]]
                        ref_desc = "、".join(names) if names else "参考图片"

                    with st.spinner("DeepSeek generating {}s prompt...".format(duration)):
                        try:
                            prompt = llm.generate_video_prompt(
                                activity_theme=st.session_state.get("quick_mode_input", ""),
                                video_script=idea.get("description", ""),
                                has_reference=has_ref,
                                ref_description=ref_desc,
                                style=st.session_state.quick_mode_style,
                                duration=duration,
                                camera_fixed=has_ref,
                            )
                            st.session_state.quick_mode_prompt = prompt
                        except Exception as e:
                            st.error("generate failed: " + str(e))

            if st.session_state.quick_mode_prompt:
                st.success("prompt ready")
                with st.expander("preview", expanded=False):
                    st.code(st.session_state.quick_mode_prompt[:500], language=None)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("back to reference", use_container_width=True):
                    st.session_state.quick_mode_prompt = ""
                    st.session_state.quick_mode_step = "reference"
                    st.rerun()
            with c2:
                if st.session_state.quick_mode_prompt:
                    if st.button("edit prompt", use_container_width=True, type="primary"):
                        st.session_state.quick_mode_step = "prompt"
                        st.rerun()
            st.divider()
'''

step5_marker = "        # Step 5: Edit Prompt + Generate"
content = content.replace(step5_marker, duration_step + "\n" + step5_marker)

with open("webui/Main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
