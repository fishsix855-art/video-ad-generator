import os
C = chr

filepath = os.path.join(os.getcwd(), "webui", "quick_app.py")

code = f"""import os, sys, time, tempfile, shutil, uuid, yaml

_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

def _load_features():
    yaml_path = os.path.join(_root, "config", "app.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            try:
                cfg = yaml.safe_load(f)
                return cfg.get("features", {{}})
            except Exception:
                pass
    return {{}}

_features = _load_features()

import streamlit as st
from app.services import llm

API_BASE = "http://127.0.0.1:8080"
if hasattr(st, "secrets"):
    import os as _os
    for _key in ["DEEPSEEK_API_KEY", "VOLCENGINE_API_KEY", "VOLCENGINE_MODEL_NAME"]:
        try:
            _val = st.secrets[_key]
            if _val: _os.environ[_key] = _val
        except Exception:
            pass

st.set_page_config(page_title="AI Video", page_icon="{C(0x25b6)}", layout="centered", initial_sidebar_state="expanded")

st.markdown("""<style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent !important;}}
    .stApp {{ background: #f8fafc; }}
    .stApp h1, .stApp h2, .stApp h3 {{ color: #0f172a; }}
    .stApp p, .stApp span, .stApp label, .stApp .stMarkdown, .stApp .stCaption {{ color: #334155; }}

    @keyframes logoReveal {{
        0%   {{ opacity: 0; transform: scale(0.95) translateY(8px); }}
        100% {{ opacity: 1; transform: scale(1) translateY(0); }}
    }}
    .logo-reveal {{ animation: logoReveal 0.6s cubic-bezier(0.23, 1, 0.32, 1) both; }}

    @keyframes contentIn {{
        0%   {{ opacity: 0; transform: translateY(12px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    .content-stagger-1 {{ animation: contentIn 0.5s 0.05s cubic-bezier(0.23,1,0.32,1) both; }}
    .content-stagger-2 {{ animation: contentIn 0.5s 0.12s cubic-bezier(0.23,1,0.32,1) both; }}
    .content-stagger-3 {{ animation: contentIn 0.5s 0.19s cubic-bezier(0.23,1,0.32,1) both; }}

    .stButton > button {{
        background: #2563eb !important; color: #fff !important; border: none !important;
        border-radius: 12px !important; font-weight: 600 !important;
        font-size: 0.875rem !important; padding: 0.55rem 1.25rem !important;
        box-shadow: 0 1px 3px rgba(37,99,235,0.15) !important;
        transition: transform 0.2s cubic-bezier(0.23,1,0.32,1), box-shadow 0.2s ease !important;
    }}
    .stButton > button:hover {{ box-shadow: 0 4px 14px rgba(37,99,235,0.25) !important; transform: translateY(-1px); }}
    .stButton > button:active {{ transform: scale(0.97); }}
    .stButton > button[kind="secondary"], .stButton > button[kind="secondary"]:hover {{
        background: #fff !important; color: #475569 !important;
        border: 1px solid #e2e8f0 !important; box-shadow: none !important;
    }}

    .stTextInput input, .stTextArea textarea {{
        background: #fff !important; border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important; color: #0f172a !important;
        padding: 0.7rem 0.85rem !important; font-size: 0.95rem !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    }}

    .idea-card {{
        background: #fff; border: 1px solid #e2e8f0;
        border-radius: 14px; padding: 22px 20px; margin-bottom: 12px;
        transition: transform 0.25s cubic-bezier(0.23,1,0.32,1), box-shadow 0.25s ease, border-color 0.25s ease;
    }}
    .idea-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
        border-color: rgba(37,99,235,0.2);
    }}

    .style-card {{
        background: #fff; border: 1px solid #e2e8f0;
        border-radius: 14px; padding: 18px 14px; text-align: center;
        transition: transform 0.25s cubic-bezier(0.23,1,0.32,1), box-shadow 0.25s ease;
    }}
    .style-card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.06); border-color: rgba(37,99,235,0.25); }}
    .style-card-selected {{
        background: #eff6ff; border: 2px solid #2563eb;
        border-radius: 14px; padding: 18px 14px; text-align: center;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.08);
    }}

    .stProgress > div > div > div {{ background: #2563eb !important; }}
    .stAlert {{ border-radius: 12px !important; }}
    .stCodeBlock {{ background: #f1f5f9 !important; border: 1px solid #e2e8f0 !important; border-radius: 12px !important; }}
    [data-testid="stSidebar"] {{ background: #fff; border-right: 1px solid #e2e8f0; }}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="logo-reveal" style="text-align:center;padding:28px 0 12px 0">
    <div style="display:inline-flex;align-items:center;justify-content:center;background:#2563eb;color:#fff;width:44px;height:44px;border-radius:12px;font-size:22px;margin-bottom:10px">{C(0x25b6)}</div>
    <h1 style="font-size:1.7rem;font-weight:700;color:#0f172a;margin:0;letter-spacing:-0.03em;line-height:1.2">AI {C(0x89c6)}{C(0x9891)}{C(0x5e7f)}{C(0x544a)}{C(0x751f)}{C(0x6210)}{C(0x5668)}</h1>
    <p style="color:#64748b;font-size:0.85rem;margin-top:4px">{C(0x8f93)}{C(0x5165)}{C(0x6d3b)}{C(0x52a8)}{C(0x4e3b)}{C(0x9898)}{C(0xff0c)} AI {C(0x81ea)}{C(0x52a8)}{C(0x751f)}{C(0x6210)}{C(0x521b)}{C(0x610f)}{C(0x65b9)}{C(0x6848)}{C(0x4e0e)}{C(0x89c6)}{C(0x9891)}</p>
</div>
""", unsafe_allow_html=True)

# Session state init
_defaults = {{
    "quick_mode_step": "input", "quick_mode_ideas": [], "quick_mode_selected": -1,
    "quick_mode_style": "", "quick_mode_duration": 8,
    "quick_mode_prompt": "", "quick_mode_final_prompt": "",
    "quick_mode_session_id": "", "quick_gen_task_id": None,
    "quick_mode_agent_steps": [], "quick_mode_agent_stream": [],
    "quick_mode_selected_idea": {{}},
}}
for _k, _v in _defaults.items():
    if _k not in st.session_state: st.session_state[_k] = _v

if not st.session_state.quick_mode_session_id:
    st.session_state.quick_mode_session_id = str(uuid.uuid4())

def _save_progress(status=""):
    try:
        if not _features.get("sqlite_enabled", False):
            return
        from app.services import database
        database.init_db()
        sid = st.session_state.get("quick_mode_session_id", "")
        if not sid: return
        database.save_task({{
            "id": sid,
            "user_input": st.session_state.get("quick_mode_input", ""),
            "creative_idea": st.session_state.get("quick_mode_selected_idea", {{}}),
            "style": st.session_state.get("quick_mode_style", ""),
            "duration": st.session_state.get("quick_mode_duration", 8),
            "prompt": st.session_state.get("quick_mode_prompt", ""),
            "final_prompt": st.session_state.get("quick_mode_final_prompt", ""),
            "status": status or st.session_state.get("quick_mode_step", "input"),
        }})
    except Exception as e:
        print(f"[SAVE ERROR] {{e}}")

# Sidebar
tab = st.sidebar.radio("{C(0x5bfc)}{C(0x822a)}", ["{C(0x5feb)}{C(0x901f)}{C(0x751f)}{C(0x6210)}", "{C(0x5386)}{C(0x53f2)}{C(0x8bb0)}{C(0x5f55)}"], key="main_tab")

if tab == "{C(0x5386)}{C(0x53f2)}{C(0x8bb0)}{C(0x5f55)}":
    sqlite_on = _features.get("sqlite_enabled", False)
    if not sqlite_on:
        st.warning("{C(0x5386)}{C(0x53f2)}{C(0x8bb0)}{C(0x5f55)}{C(0x529f)}{C(0x80fd)}{C(0x5c1a)}{C(0x672a)}{C(0x5f00)}{C(0x542f)}{C(0x3002)}{C(0x8bf7)}{C(0x5728)} config/app.yaml {C(0x4e2d)}{C(0x8bbe)}{C(0x7f6e)} sqlite_enabled: true")
    else:
        try:
            from app.services import database
            tasks = database.list_tasks(limit=50)
            if not tasks:
                st.info("{C(0x6682)}{C(0x65e0)}{C(0x5386)}{C(0x53f2)}{C(0x8bb0)}{C(0x5f55)}{C(0xff0c)}{C(0x751f)}{C(0x6210)}{C(0x89c6)}{C(0x9891)}{C(0x540e)}{C(0x4f1a)}{C(0x81ea)}{C(0x52a8)}{C(0x4fdd)}{C(0x5b58)}")
            else:
                for t in tasks:
                    created = t.get("created_at", "")[:16]
                    user_input = t.get("user_input", "")
                    style = t.get("style", "{C(0x65e0)}")
                    status = t.get("status", "")
                    with st.expander(f"{{created}} | {{user_input[:25]}} | {{style}}", expanded=False):
                        task_detail = database.get_task(t["id"])
                        if task_detail:
                            st.caption(f"Status: **{{status}}** | Duration: **{{task_detail.get('duration','?')}}s**")
                            prompt = task_detail.get("final_prompt", "") or task_detail.get("prompt", "")
                            if prompt:
                                with st.expander("{C(0x67e5)}{C(0x770b)}{C(0x63d0)}{C(0x793a)}{C(0x8bcd)}", expanded=False):
                                    st.text_area("", value=prompt, height=150, disabled=True, key=f"hist_p_{{t['id']}}")
        except Exception as e:
            st.error(f"{C(0x52a0)}{C(0x8f7d)}{C(0x5931)}{C(0x8d25)}: {{e}}")
    st.stop()

# Step progress
_steps_order = ["input", "choose", "confirm", "result"]
_step_labels = ["{C(0x8f93)}{C(0x5165)}", "{C(0x9009)}{C(0x65b9)}{C(0x6848)}", "{C(0x786e)}{C(0x8ba4)}", "{C(0x7ed3)}{C(0x679c)}"]
_cur = _steps_order.index(st.session_state.quick_mode_step) if st.session_state.quick_mode_step in _steps_order else 0
_html = '<div style="display:flex;gap:6px;margin-bottom:20px;justify-content:center">'
for _si, _sl in enumerate(_step_labels):
    if _si < _cur:
        _html += f'<span style="background:#10b981;color:#fff;padding:4px 14px;border-radius:12px;font-size:11px;opacity:0.7">{C(0x2713)} {{_sl}}</span>'
    elif _si == _cur:
        _html += f'<span style="background:#6366f1;color:#fff;padding:4px 14px;border-radius:12px;font-size:11px;font-weight:700">{{_sl}}</span>'
    else:
        _html += f'<span style="background:#e2e8f0;color:#94a3b8;padding:4px 14px;border-radius:12px;font-size:11px">{{_sl}}</span>'
_html += '</div>'
st.markdown(_html, unsafe_allow_html=True)

# ============================================================
# STAGE 1: INPUT
# ============================================================
if st.session_state.quick_mode_step == "input":
    templates = [
        ("{C(0x65b0)}{C(0x5e97)}{C(0x5f00)}{C(0x4e1a)}", "{C(0x7535)}{C(0x4fe1)}{C(0x8425)}{C(0x4e1a)}{C(0x5385)}{C(0x65b0)}{C(0x5e97)}{C(0x5f00)}{C(0x4e1a)}{C(0x5927)}{C(0x916c)}{C(0x5bbe)}"),
        ("{C(0x8282)}{C(0x65e5)}{C(0x4fc3)}{C(0x9500)}", "{C(0x4e2d)}{C(0x79cb)}{C(0x56fd)}{C(0x5e86)}{C(0x53cc)}{C(0x8282)}{C(0x7279)}{C(0x60e0)}"),
        ("{C(0x4ee5)}{C(0x65e7)}{C(0x6362)}{C(0x65b0)}", "{C(0x65e7)}{C(0x624b)}{C(0x673a)}{C(0x6362)}{C(0x65b0)}{C(0x673a)}{C(0xff0c)}{C(0x6700)}{C(0x9ad8)}{C(0x6298)}{C(0x4ef7)}2000{C(0x5143)}"),
    ]
    st.markdown("### {C(0x5feb)}{C(0x6377)}{C(0x6a21)}{C(0x677f)}")
    tc1, tc2, tc3 = st.columns(3)
    for i, (label, tpl) in enumerate(templates):
        with [tc1, tc2, tc3][i]:
            if st.button(label, key=f"tpl_{{i}}", use_container_width=True):
                st.session_state.quick_mode_input = tpl

    col1, col2 = st.columns([3, 1])
    with col1:
        quick_input = st.text_input("{C(0x6d3b)}{C(0x52a8)}{C(0x63cf)}{C(0x8ff0)}", placeholder="{C(0x6216)}{C(0x70b9)}{C(0x51fb)}{C(0x4e0a)}{C(0x65b9)}{C(0x6a21)}{C(0x677f)}{C(0x5feb)}{C(0x901f)}{C(0x586b)}{C(0x5165)}", key="quick_mode_input", label_visibility="collapsed")
    with col2:
        if st.button("{C(0x751f)}{C(0x6210)}{C(0x521b)}{C(0x610f)}{C(0x65b9)}{C(0x6848)}", use_container_width=True, type="primary", disabled=not quick_input):
            import os as _os
            if not _os.environ.get("DEEPSEEK_API_KEY"):
                try:
                    from app.config import config as _cfg
                    _k = _cfg.app.get("deepseek_api_key","")
                    if _k: _os.environ["DEEPSEEK_API_KEY"] = _k
                except: pass

            # Streaming callback
            st.session_state.quick_mode_agent_stream = []
            def _cb(evt):
                st.session_state.quick_mode_agent_stream.append(evt)

            with st.status("Agent {C(0x601d)}{C(0x8003)}{C(0x4e2d)}...", expanded=True) as _status:
                agent_on = _features.get("agent_enabled", False)
                if agent_on:
                    try:
                        from app.services import agent as _ag
                        from app.services.tools import TOOL_DEFINITIONS, TOOL_HANDLERS
                        import json as _json

                        system_prompt = _json.dumps({{
                            "task": "{C(0x751f)}{C(0x6210)}6{C(0x4e2a)}{C(0x521b)}{C(0x610f)}{C(0x65b9)}{C(0x6848)}",
                            "steps": [
                                "search_product_kb",
                                "search_relevant_cases",
                                "{C(0x751f)}{C(0x6210)}JSON",
                                "evaluate_creative_ideas",
                                "{C(0x8f93)}{C(0x51fa)}",
                            ],
                            "output": "JSON {{title, style, description}} description 80-120{C(0x5b57)}",
                        }}, ensure_ascii=False)
                        agent_result = _ag.run_agent(
                            system_prompt=system_prompt,
                            user_message=f"{C(0x6d3b)}{C(0x52a8)}: {{quick_input}}",
                            tools=TOOL_DEFINITIONS,
                            tool_handlers=TOOL_HANDLERS,
                            max_steps=10,
                            session_id=st.session_state.quick_mode_session_id,
                            stream_callback=_cb,
                        )

                        # Check interrupt
                        if agent_result.get("status") == "waiting_user":
                            st.session_state.quick_mode_ideas = agent_result.get("options", [])
                            st.session_state.quick_mode_agent_steps = agent_result.get("steps", [])
                            st.session_state.quick_mode_step = "choose"
                            _save_progress("choosing")
                            st.rerun()

                        answer = agent_result.get("answer", "")
                        ideas = []
                        try:
                            if "```" in answer: answer = answer.split("```")[1]; answer = answer.replace("json","",1).strip()
                            raw = _json.loads(answer) if answer.startswith("[") else _json.loads("[" + answer + "]")
                            for ri in raw:
                                if isinstance(ri, dict) and "title" in ri:
                                    ideas.append({{"title": ri.get("title",""), "description": ri.get("description",""), "style": ri.get("style","")}})
                        except: pass

                        if ideas and len(ideas) >= 3:
                            st.session_state.quick_mode_ideas = ideas[:6]
                            st.session_state.quick_mode_agent_steps = agent_result.get("steps", [])
                            st.session_state.quick_mode_step = "choose"
                            _save_progress("choosing")
                            st.rerun()
                    except Exception as e:
                        st.warning(f"Agent {C(0x6a21)}{C(0x5f0f)}{C(0x5931)}{C(0x8d25)}: {{e}}")

                # Fallback: non-Agent
                ideas = llm.generate_creative_ideas(quick_input)
                st.session_state.quick_mode_ideas = ideas
                st.session_state.quick_mode_agent_steps = []
                st.session_state.quick_mode_step = "choose"
                _save_progress("choosing")
                st.rerun()

# ============================================================
# STAGE 2: CHOOSE
# ============================================================
elif st.session_state.quick_mode_step == "choose":
    agent_steps = st.session_state.get("quick_mode_agent_steps", [])
    if agent_steps:
        with st.expander("Agent Reasoning (" + str(len(agent_steps)) + " steps)", expanded=True):
            for s in agent_steps:
                st.caption("Step " + str(s.get("step","?")) + ": " + str(s.get("tool","thinking")))
                if s.get("result"):
                    st.code(str(s.get("result",""))[:400], language="json")

    ideas = st.session_state.quick_mode_ideas
    st.markdown("### {C(0x9009)}{C(0x62e9)}{C(0x4e00)}{C(0x4e2a)}{C(0x521b)}{C(0x610f)}{C(0x65b9)}{C(0x6848)}")
    for row_start in range(0, len(ideas), 3):
        cols = st.columns(3)
        for ci in range(3):
            idx = row_start + ci
            if idx >= len(ideas): break
            idea = ideas[idx]
            with cols[ci]:
                st.markdown(f"""<div class="idea-card content-stagger-{{(idx%3)+1}}">
                    <div style="font-weight:700;font-size:15px;margin-bottom:4px;color:#0f172a">{{idea.get("title","")}}</div>
                    <div style="font-size:10px;color:#94a3b8;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.08em">{{idea.get("style","")}}</div>
                    <div style="font-size:12px;color:#64748b;line-height:1.5">{{idea.get("description","")}}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("{C(0x9009)}{C(0x62e9)}{C(0x6b64)}{C(0x65b9)}{C(0x6848)}", key=f"sel_{{idx}}", use_container_width=True):
                    st.session_state.quick_mode_selected = idx
                    st.session_state.quick_mode_selected_idea = idea
                    
                    # Resume Agent to generate storyboard
                    try:
                        from app.services import agent as _ag
                        from app.services.tools import TOOL_DEFINITIONS, TOOL_HANDLERS
                        resume_state = {{"session_id": st.session_state.quick_mode_session_id}}
                        system_prompt = f"You are a video prompt engineer. User chose: {{idea['title']}} (style: {{idea.get('style','')}}). Generate a detailed storyboard prompt with time slices (0.0-X.X{C(0x79d2)}), 9:16 portrait, HD quality. Minimum 4 time slices, minimum 300 characters."
                        ag_r = _ag.run_agent(
                            system_prompt=system_prompt,
                            user_message=f"Generate storyboard for: {{idea['description']}}",
                            tools=TOOL_DEFINITIONS,
                            tool_handlers=TOOL_HANDLERS,
                            max_steps=5,
                        )
                        prompt_text = ag_r.get("answer", "").strip()
                        if prompt_text:
                            st.session_state.quick_mode_prompt = prompt_text
                    except Exception as e:
                        st.warning(f"Storyboard generation failed: {{e}}")
                    
                    st.session_state.quick_mode_step = "confirm"
                    _save_progress("confirming")
                    st.rerun()

    if st.button("{C(0x8fd4)}{C(0x56de)}{C(0x4fee)}{C(0x6539)}{C(0x63cf)}{C(0x8ff0)}"):
        st.session_state.quick_mode_step = "input"; st.session_state.quick_mode_ideas = []; st.rerun()

# ============================================================
# STAGE 3: CONFIRM
# ============================================================
elif st.session_state.quick_mode_step == "confirm":
    idea = st.session_state.get("quick_mode_selected_idea", {{}})
    st.info(f"{C(0x5df2)}{C(0x9009)}{C(0x65b9)}{C(0x6848)}: **{{idea.get('title','')}}**")

    # Quick style & duration
    c1, c2 = st.columns(2)
    with c1:
        style_opts = ["{C(0x5199)}{C(0x5b9e)}{C(0x5546)}{C(0x4e1a)}", "{C(0x6e29)}{C(0x99a8)}{C(0x6cbb)}{C(0x6108)}", "{C(0x79d1)}{C(0x6280)}{C(0x672a)}{C(0x6765)}", "{C(0x52a8)}{C(0x6f2b)}{C(0x4e8c)}{C(0x6b21)}{C(0x5143)}", "{C(0x56fd)}{C(0x98ce)}{C(0x53e4)}{C(0x97f5)}", "{C(0x6f6e)}{C(0x6d41)}{C(0x5feb)}{C(0x65f6)}{C(0x5c1a)}"]
        style = st.selectbox("{C(0x89c6)}{C(0x9891)}{C(0x98ce)}{C(0x683c)}", style_opts, index=0, key="confirm_style")
        st.session_state.quick_mode_style = style
    with c2:
        duration = st.slider("{C(0x65f6)}{C(0x957f)}(s)", 4, 15, st.session_state.quick_mode_duration, key="confirm_dur")
        st.session_state.quick_mode_duration = duration

    # Storyboard display
    prompt_text = st.session_state.get("quick_mode_prompt", "")
    if not prompt_text:
        # Generate if not yet
        try:
            from app.services import agent as _ag
            from app.services.tools import TOOL_DEFINITIONS, TOOL_HANDLERS
            system_prompt = f"You are a video prompt engineer. Generate a storyboard prompt with time slices. Style: {{style}}. Duration: {{duration}}s. 9:16 portrait, HD, minimum 4 slices."
            ag_r = _ag.run_agent(
                system_prompt=system_prompt,
                user_message=f"Topic: {{idea.get('description','')}}. Style: {{style}}. Duration: {{duration}}s",
                tools=TOOL_DEFINITIONS, tool_handlers=TOOL_HANDLERS, max_steps=5,
            )
            prompt_text = ag_r.get("answer", "").strip()
            if prompt_text: st.session_state.quick_mode_prompt = prompt_text
        except Exception as e:
            prompt_text = f"[{C(0x63d0)}{C(0x793a)}{C(0x8bcd)}{C(0x751f)}{C(0x6210)}{C(0x5931)}{C(0x8d25)}: {{e}}]"

    st.markdown("### {C(0x89c6)}{C(0x9891)}{C(0x63d0)}{C(0x793a)}{C(0x8bcd)}")
    edited = st.text_area("", value=prompt_text, height=200, key="edit_prompt")
    st.session_state.quick_mode_prompt = edited

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("{C(0x8fd4)}{C(0x56de)}{C(0x9009)}{C(0x65b9)}{C(0x6848)}", use_container_width=True):
            st.session_state.quick_mode_step = "choose"; st.rerun()
    with c2:
        if st.button("{C(0x91cd)}{C(0x65b0)}{C(0x751f)}{C(0x6210)}", use_container_width=True):
            st.session_state.quick_mode_prompt = ""; st.rerun()
    with c3:
        if st.button("{C(0x786e)}{C(0x8ba4)}{C(0xff0c)}{C(0x751f)}{C(0x6210)}{C(0x89c6)}{C(0x9891)}", use_container_width=True, type="primary"):
            st.session_state.quick_mode_final_prompt = edited
            st.session_state.quick_mode_step = "result"
            _save_progress("generating")
            st.rerun()

# ============================================================
# STAGE 4: RESULT
# ============================================================
elif st.session_state.quick_mode_step == "result":
    final_prompt = st.session_state.get("quick_mode_final_prompt", "")
    st.info("{C(0x6b63)}{C(0x5728)}{C(0x751f)}{C(0x6210)}{C(0x89c6)}{C(0x9891)}...")
    with st.expander("{C(0x67e5)}{C(0x770b)}{C(0x63d0)}{C(0x793a)}{C(0x8bcd)}", expanded=False):
        st.code(final_prompt[:500])

    # Video generation
    import requests as _req
    gen_state = 0
    try:
        payload = {{
            "video_subject": st.session_state.get("quick_mode_input", ""),
            "video_script": final_prompt,
            "duration": st.session_state.quick_mode_duration,
            "style": st.session_state.quick_mode_style,
        }}
        r = _req.post(f"{{API_BASE}}/api/v1/videos", json=payload, timeout=120)
        if r.status_code == 200:
            task = r.json().get("data", {{}})
            tid = task.get("task_id", "")
            st.session_state.quick_gen_task_id = tid
            gen_state = 1
        else:
            st.error(f"Generation failed: {{r.status_code}} - {{r.text[:200]}}")
    except Exception as e:
        st.error(f"API error: {{e}}")

    # Poll for completion
    if gen_state == 1:
        tid = st.session_state.quick_gen_task_id
        bar = st.progress(0, "Generating...")
        for progress in range(1, 101, 5):
            time.sleep(1.5)
            bar.progress(progress, f"Generating... {{progress}}%")
            try:
                r = _req.get(f"{{API_BASE}}/api/v1/videos/{{tid}}", timeout=10)
                if r.status_code == 200:
                    data = r.json().get("data", {{}})
                    state = data.get("state", -1)
                    if state < 0:
                        bar.progress(100, "Complete!")
                        gen_state = 2
                        break
            except: pass
        if gen_state != 2:
            st.warning("{C(0x751f)}{C(0x6210)}{C(0x8d85)}{C(0x65f6)}{C(0xff0c)}{C(0x8bf7)}{C(0x5237)}{C(0x65b0)}")

    # Feedback
    st.divider()
    st.caption("{C(0x60f3)}{C(0x8c03)}{C(0x6574)}{C(0x4ec0)}{C(0x4e48)}? {C(0x76f4)}{C(0x63a5)}{C(0x544a)}{C(0x8bc9)}{C(0x6211)}:")
    fb_c1, fb_c2 = st.columns([3,1])
    with fb_c1:
        fb_text = st.text_input("", placeholder="{C(0x4f8b)}{C(0x5982)}: {C(0x52a0)}{C(0x5b57)}{C(0x5e55)}{C(0x3001)}{C(0x6362)}{C(0x98ce)}{C(0x683c)}{C(0x3001)}{C(0x91cd)}{C(0x751f)}{C(0x63d0)}{C(0x793a)}{C(0x8bcd)}", key="quick_fb", label_visibility="collapsed")
    with fb_c2:
        if st.button("{C(0x53d1)}{C(0x9001)}", key="fb_send", use_container_width=True, disabled=not fb_text):
            with st.spinner("Agent {C(0x5206)}{C(0x6790)}{C(0x4e2d)}..."):
                context = {{
                    "style": st.session_state.quick_mode_style,
                    "duration": st.session_state.quick_mode_duration,
                    "prompt": st.session_state.quick_mode_prompt,
                }}
                fb_result = llm.process_feedback_with_agent(fb_text, context)
            
            action = fb_result.get("action", "done")
            reply = fb_result.get("reply", "")
            st.success(reply)
            
            if action == "restyle":
                st.session_state.quick_mode_step = "choose"; st.rerun()
            elif action == "regen_prompt":
                st.session_state.quick_mode_step = "confirm"; st.session_state.quick_mode_prompt = ""; st.rerun()
            elif action in ["add_subtitle", "trim_video", "concat_videos"]:
                st.info(f"Post-production: {{action}}")
            elif action == "done":
                pass

    if st.button("{C(0x91cd)}{C(0x65b0)}{C(0x5f00)}{C(0x59cb)}"):
        for _k in _defaults:
            if _k in st.session_state:
                del st.session_state[_k]
        st.rerun()

print("[APP] quick_app.py v4.0-4stage loaded")
"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)
print("Generated quick_app.py. Size:", len(code))
