import os, sys, time

_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

import streamlit as st
from app.services import llm

# API base URL (auto-detect: local dev or deployment)
API_BASE = os.environ.get("API_BASE_URL", "http://127.0.0.1:8080")

st.set_page_config(page_title="AI Video", page_icon="", layout="centered", initial_sidebar_state="collapsed")

# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    #MainMenu, footer, header[data-testid="stHeader"] {visibility: hidden;}

    .stApp { background: linear-gradient(180deg, #fafbfc 0%, #f0f2f5 100%); }

    .stApp, .stApp h2, .stApp h3, .stApp h4,
    .stApp p, .stApp span, .stApp label, .stApp div,
    .stApp .stMarkdown, .stApp .stCaption { color: #1e293b !important; }

    /* Logo reveal */
    @keyframes logoReveal {
        0%   { opacity: 0; transform: scale(0.95) translateY(8px); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
    }
    .logo-reveal { animation: logoReveal 0.6s cubic-bezier(0.23, 1, 0.32, 1) both; }

    /* Content stagger */
    @keyframes contentIn {
        0%   { opacity: 0; transform: translateY(12px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .content-stagger-1 { animation: contentIn 0.5s 0.05s cubic-bezier(0.23,1,0.32,1) both; }
    .content-stagger-2 { animation: contentIn 0.5s 0.12s cubic-bezier(0.23,1,0.32,1) both; }
    .content-stagger-3 { animation: contentIn 0.5s 0.19s cubic-bezier(0.23,1,0.32,1) both; }

    /* Primary button */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
        color: #fff !important; border: none !important;
        border-radius: 10px !important; font-weight: 600 !important;
        font-size: 0.875rem !important; padding: 0.55rem 1.2rem !important;
        box-shadow: 0 2px 8px rgba(37,99,235,0.2) !important;
        transition: transform 0.2s cubic-bezier(0.23,1,0.32,1), box-shadow 0.2s ease !important;
    }
    .stButton > button:hover {
        box-shadow: 0 4px 16px rgba(37,99,235,0.3) !important;
        transform: translateY(-1px);
    }
    .stButton > button:active { transform: scale(0.97); }

    .stButton > button[kind="secondary"], .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.8) !important; color: #475569 !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        border-radius: 10px !important; color: #1e293b !important;
        padding: 0.7rem 0.85rem !important; font-size: 0.95rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important; background: #fff !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #94a3b8 !important; }

    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(0,0,0,0.08) !important; border-radius: 10px !important;
    }

    .stProgress > div > div > div { background: linear-gradient(90deg, #2563eb, #3b82f6) !important; }
    .stAlert { border-radius: 12px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important; }
    hr { border-color: rgba(0,0,0,0.06) !important; }
    .stCodeBlock { background: #f1f5f9 !important; border: 1px solid rgba(0,0,0,0.06) !important; border-radius: 10px !important; }
    .stSlider [data-testid="stThumbValue"] { background: #2563eb !important; color: #fff !important; border-radius: 6px !important; }

    /* Idea cards */
    .idea-card {
        background: #fff; border: 1px solid rgba(0,0,0,0.06);
        border-radius: 14px; padding: 22px 20px; margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        transition: transform 0.25s cubic-bezier(0.23,1,0.32,1), box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .idea-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
        border-color: rgba(37,99,235,0.2);
    }

    /* Style cards */
    .style-card {
        background: #fff; border: 1px solid rgba(0,0,0,0.06);
        border-radius: 14px; padding: 18px 14px; text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        transition: transform 0.25s cubic-bezier(0.23,1,0.32,1), box-shadow 0.25s ease;
    }
    .style-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        border-color: rgba(37,99,235,0.25);
    }
    .style-card-selected {
        background: #eff6ff; border: 2px solid #2563eb;
        border-radius: 14px; padding: 18px 14px; text-align: center;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.08);
    }

    /* Floating blobs */
    .hero-blob {
        position: fixed; border-radius: 50%; filter: blur(80px);
        opacity: 0.07; pointer-events: none; z-index: 0;
        animation: floatBlob 22s ease-in-out infinite;
    }
    @keyframes floatBlob {
        0%,100% { transform: translate(0,0) scale(1); }
        25%  { transform: translate(40px,-25px) scale(1.06); }
        50%  { transform: translate(-25px,15px) scale(0.94); }
        75%  { transform: translate(15px,35px) scale(1.03); }
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# BACKGROUND + LOGO
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-blob" style="width:420px;height:420px;background:#2563eb;top:-120px;right:-100px;"></div>
<div class="hero-blob" style="width:320px;height:320px;background:#3b82f6;bottom:-100px;left:-80px;animation-delay:-9s;"></div>
<div class="hero-blob" style="width:260px;height:260px;background:#6366f1;top:45%;left:55%;animation-delay:-16s;"></div>

<div class="logo-reveal" style="text-align:center;padding:40px 0 12px 0;position:relative;z-index:1">
    <div style="display:inline-block;background:linear-gradient(135deg,#2563eb,#3b82f6);color:#fff;width:56px;height:56px;border-radius:15px;line-height:56px;font-size:28px;font-weight:800;box-shadow:0 6px 24px rgba(37,99,235,0.3);margin-bottom:4px">T</div>
    <div style="font-size:0.7rem;color:#94a3b8;letter-spacing:0.2em;margin-bottom:8px;margin-top:6px">TELECOM VIDEO</div>
    <h1 style="font-size:1.9rem;font-weight:700;color:#0f172a;margin:0;letter-spacing:-0.03em;line-height:1.2">视频广告生成器</h1>
    <p style="color:#64748b;font-size:0.85rem;margin-top:4px;font-weight:400">输入活动描述，AI 自动生成创意方案与视频</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
_defaults = {
    "quick_mode_step": "input", "quick_mode_ideas": [], "quick_mode_selected": -1,
    "quick_mode_style": "", "quick_mode_refs": [], "quick_mode_prompt": "",
    "quick_mode_duration": 8, "quick_gen_task_id": None, "quick_mode_final_prompt": "",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state: st.session_state[_k] = _v

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
import os as _os

if st.session_state.quick_mode_step == "input":
    # Scene templates
    templates = [
        ("新店开业", "电信营业厅新店开业大酬宾，进店办理宽带送小家电，前100名额外赠送50元话费"),
        ("节日促销", "中秋国庆双节特惠，充值满200送100，5G套餐半价起，限时7天"),
        ("周末特惠", "本周末限时活动，进店即送精美礼品，办理融合套餐享折上折"),
        ("以旧换新", "旧手机换新机，最高折价2000元，旧机不论品牌均可参与"),
    ]
    st.markdown("### 快捷模板")
    tc1, tc2, tc3, tc4 = st.columns(4)
    for i, (label, tpl) in enumerate(templates):
        with [tc1, tc2, tc3, tc4][i]:
            if st.button(label, key=f"tpl_{i}", use_container_width=True):
                st.session_state.quick_mode_input = tpl
                st.session_state.quick_input_tpl = tpl

    col1, col2 = st.columns([3, 1])
    with col1:
        tpl_val = st.session_state.get("quick_input_tpl", "")
        if "quick_mode_input" not in st.session_state:
            st.session_state.quick_mode_input = tpl_val
        quick_input = st.text_input("活动描述", placeholder="或点击上方模板快速填入", key="quick_mode_input", label_visibility="collapsed")
    with col2:
        if st.button("生成创意方案", use_container_width=True, type="primary", disabled=not quick_input):
            with st.spinner("DeepSeek 正在生成 6 个创意方案..."):
                try:
                    ideas = llm.generate_creative_ideas(quick_input)
                    st.session_state.quick_mode_ideas = ideas
                    st.session_state.quick_mode_step = "choose"; st.session_state.quick_mode_selected = -1
                    st.rerun()
                except Exception as e:
                    st.error("生成创意失败: " + str(e))

elif st.session_state.quick_mode_step == "choose":
    ideas = st.session_state.quick_mode_ideas
    emoji_map = {"warm":"","humor":"","direct":"","suspense":"","scenic":"","social":""}
    label_map = {"warm":"温情走心","humor":"幽默吸睛","direct":"直给促销","suspense":"悬念反转","scenic":"场景故事","social":"口碑推荐"}
    st.markdown("### 选择一个创意方案")
    for row_start in range(0, len(ideas), 3):
        cols = st.columns(3)
        for ci in range(3):
            idx = row_start + ci
            if idx >= len(ideas): break
            idea = ideas[idx]
            emoji = emoji_map.get(idea.get("style",""),"")
            style_label = label_map.get(idea.get("style",""),idea.get("style",""))
            stagger = (idx % 3) + 1
            with cols[ci]:
                st.markdown(f"""<div class="idea-card content-stagger-{stagger}">
                    <div style="font-size:24px;margin-bottom:6px">{emoji}</div>
                    <div style="font-weight:700;font-size:15px;margin-bottom:4px;color:#0f172a">{idea.get("title","")}</div>
                    <div style="font-size:10px;color:#94a3b8;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.08em">{style_label}</div>
                    <div style="font-size:12px;color:#64748b;line-height:1.5">{idea.get("description","")}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("选择此方案", key=f"sel_{idx}", use_container_width=True):
                    st.session_state.quick_mode_selected = idx
                    st.session_state.quick_mode_step = "style"; st.rerun()
    if st.button("返回修改描述"):
        st.session_state.quick_mode_step = "input"; st.session_state.quick_mode_ideas = []; st.rerun()

elif st.session_state.quick_mode_step == "style":
    if st.session_state.quick_mode_selected >= 0:
        idea = st.session_state.quick_mode_ideas[st.session_state.quick_mode_selected]
        st.info(f"已选方案: **{idea.get('title','')}**")
    st.markdown("### 选择视频风格")
    styles = [("","写实商业广告","明亮干净的商业场景"),("","温馨治愈","柔光、暖色调、治愈感"),("","科技未来感","霓虹灯效、赛博朋克"),("","动漫二次元","二次元角色、卡通渲染"),("","国风古韵","水墨意境、中式美学"),("","时尚快消","明快节奏、潮流配色")]
    for row_start in range(0,6,3):
        cols = st.columns(3)
        for ci in range(3):
            idx = row_start+ci
            if idx>=6: break
            emoji,name,desc = styles[idx]
            selected = st.session_state.quick_mode_style == name
            stagger = (idx%3)+1
            cls = "style-card-selected" if selected else "style-card"
            with cols[ci]:
                st.markdown(f"""<div class="{cls} content-stagger-{stagger}">
                    <div style="font-size:32px">{emoji}</div>
                    <div style="font-weight:700;font-size:14px;margin-top:6px;color:#0f172a">{name}</div>
                    <div style="font-size:11px;color:#94a3b8;margin-top:3px">{desc}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("选择",key=f"sty_{idx}",use_container_width=True,disabled=selected):
                    st.session_state.quick_mode_style = name; st.rerun()
    c1,c2 = st.columns(2)
    with c1:
        if st.button("返回选创意", use_container_width=True): st.session_state.quick_mode_step = "choose"; st.rerun()
    with c2:
        if st.button("下一步：添加参考图", use_container_width=True, type="primary", disabled=not st.session_state.quick_mode_style):
            st.session_state.quick_mode_step = "reference"; st.rerun()

elif st.session_state.quick_mode_step == "reference":
    if st.session_state.quick_mode_selected >= 0:
        idea = st.session_state.quick_mode_ideas[st.session_state.quick_mode_selected]
        st.info(f"方案: **{idea.get('title','')}** | 风格: **{st.session_state.quick_mode_style}**")
    st.markdown("### 参考图（可选）")
    st.caption("上传门店照片、产品图等，AI 会根据图片名称生成对应的提示词")
    refs = st.session_state.quick_mode_refs
    if refs:
        st.markdown("**已添加：**")
        for ri,ref in enumerate(refs):
            c1,c2,c3=st.columns([2,5,1])
            with c1: st.markdown(f"**{ref.get('name','未命名')}**")
            with c2:
                if ref.get("path"): st.caption(ref["path"].split("\\")[-1][:40])
            with c3:
                if st.button("",key=f"del_ref_{ri}",help="删除"): st.session_state.quick_mode_refs.pop(ri); st.rerun()
    with st.popover("+ 添加参考图", use_container_width=False):
        ref_name = st.text_input("图片名称", placeholder="例如：电信营业厅门店照片", key="new_ref_name")
        ref_file = st.file_uploader("选择图片", type=["jpg","jpeg","png","webp"], key="new_ref_file", label_visibility="collapsed")
        if ref_file and ref_name:
            if st.button("保存", use_container_width=True, type="primary", key="save_ref_btn"):
                save_dir = _os.path.join("storage","references")
                _os.makedirs(save_dir, exist_ok=True)
                save_path = _os.path.join(save_dir, ref_file.name)
                with open(save_path,"wb") as f: f.write(ref_file.getbuffer())
                st.session_state.quick_mode_refs.append({"name":ref_name,"path":save_path}); st.rerun()
    st.divider()
    c1,c2,c3=st.columns([1,1,1])
    with c1:
        if st.button("返回选风格",use_container_width=True): st.session_state.quick_mode_step="style"; st.rerun()
    with c2:
        if st.button("跳过参考图",use_container_width=True):
            st.session_state.quick_mode_refs=[]; st.session_state.quick_mode_step="duration"; st.session_state.quick_mode_prompt=""; st.rerun()
    with c3:
        if st.button("下一步：选择时长",use_container_width=True,type="primary"):
            st.session_state.quick_mode_step="duration"; st.session_state.quick_mode_prompt=""; st.rerun()

elif st.session_state.quick_mode_step == "duration":
    if st.session_state.quick_mode_selected>=0:
        idea = st.session_state.quick_mode_ideas[st.session_state.quick_mode_selected]
        st.info(f"方案: **{idea.get('title','')}** | 风格: **{st.session_state.quick_mode_style}**")
    st.markdown("### 选择视频时长")
    duration = st.slider("视频时长（秒）",4,12,st.session_state.quick_mode_duration,1,help="最大 12 秒")
    st.session_state.quick_mode_duration = duration
    if st.session_state.quick_mode_prompt:
        st.success(f"提示词已生成（{duration} 秒）")
        with st.expander("预览",expanded=False): st.code(st.session_state.quick_mode_prompt[:500])
    c1,c2,c3=st.columns([1,1,1])
    with c1:
        if st.button("返回参考图",use_container_width=True): st.session_state.quick_mode_prompt=""; st.session_state.quick_mode_step="reference"; st.rerun()
    with c2:
        if not st.session_state.quick_mode_prompt:
            if st.button("生成提示词",use_container_width=True,type="primary"):
                if st.session_state.quick_mode_selected>=0:
                    idea = st.session_state.quick_mode_ideas[st.session_state.quick_mode_selected]
                    has_ref = len(st.session_state.quick_mode_refs)>0
                    ref_desc=""
                    if has_ref:
                        names=[r["name"] for r in st.session_state.quick_mode_refs if r["name"]]
                        ref_desc="、".join(names) if names else "参考图片"
                    with st.spinner(f"DeepSeek 正在生成 {duration} 秒分镜提示词..."):
                        try:
                            prompt = llm.generate_video_prompt(
                                activity_theme=st.session_state.get("quick_mode_input",""),
                                video_script=idea.get("description",""),
                                has_reference=has_ref, ref_description=ref_desc,
                                style=st.session_state.quick_mode_style, duration=duration, camera_fixed=has_ref)
                            st.session_state.quick_mode_prompt = prompt; st.rerun()
                        except Exception as e: st.error("生成提示词失败: "+str(e))
    with c3:
        if st.session_state.quick_mode_prompt:
            if st.button("编辑提示词",use_container_width=True,type="primary"): st.session_state.quick_mode_step="prompt"; st.rerun()
    st.divider()

elif st.session_state.quick_mode_step == "prompt":
    if st.session_state.quick_mode_selected>=0:
        idea = st.session_state.quick_mode_ideas[st.session_state.quick_mode_selected]
        st.info(f"方案: **{idea.get('title','')}** | 风格: **{st.session_state.quick_mode_style}**")
    if not st.session_state.quick_mode_prompt:
        st.warning("提示词尚未生成，请返回上一步")
        if st.button("返回"): st.session_state.quick_mode_step="duration"; st.rerun()
    else:
        st.markdown("### 视频分镜提示词（可编辑）")
        edited = st.text_area("提示词",value=st.session_state.quick_mode_prompt,height=350,key="quick_mode_edited_prompt",label_visibility="collapsed")
        c1,c2,c3=st.columns([1,1,1])
        with c1:
            if st.button("返回",use_container_width=True): st.session_state.quick_mode_step="duration"; st.rerun()
        with c2:
            if st.button("重新生成",use_container_width=True): st.session_state.quick_mode_prompt=""; st.rerun()
        with c3:
            if st.button("确认生成视频",use_container_width=True,type="primary"):
                st.session_state.quick_mode_final_prompt=edited; st.session_state.quick_mode_step="generating"; st.session_state.quick_gen_task_id=None; st.rerun()
        st.divider()

elif st.session_state.quick_mode_step == "generating":
    final_prompt = st.session_state.get("quick_mode_final_prompt","")
    st.info("正在生成视频...")
    with st.expander("查看提示词",expanded=False): st.code(final_prompt[:300]+"...")
    import requests as _req
    if not st.session_state.quick_gen_task_id:
        try:
            r = _req.post(f"{API_BASE}/api/v1/videos",json={
                "video_subject":st.session_state.get("quick_mode_input","视频"),
                "video_source":"seedance","video_script_prompt":final_prompt,
                "video_aspect":"9:16","video_concat_mode":"random",
                "video_clip_duration":st.session_state.get("quick_mode_duration",8),"language":"zh-CN"},timeout=30)
            st.session_state.quick_gen_task_id = r.json()["data"]["task_id"]; st.rerun()
        except Exception as e:
            st.error("提交任务失败: "+str(e))
            if st.button("返回修改"): st.session_state.quick_mode_step="prompt"; st.rerun()
    else:
        tid = st.session_state.quick_gen_task_id
        try:
            r = _req.get(f"{API_BASE}/api/v1/tasks/{tid}",timeout=10)
            task = r.json().get("data",{})
            state = task.get("state",-1); progress = task.get("progress",0)
            st.progress(progress/100.0,f"进度: {progress}%")
            if state == 1:
                st.success("视频生成完成")
                for idx,v in enumerate(task.get("videos",[]),1):
                    video_url = f"{API_BASE}/tasks/{tid}/final-{idx}.mp4"
                    st.video(video_url)
                    # Download button
                    download_url = f"{API_BASE}/download/{tid}/final-{idx}.mp4"
                    st.markdown(f'<a href="{download_url}" download style="text-decoration:none"><button style="background:#2563eb;color:#fff;border:none;border-radius:8px;padding:8px 20px;font-weight:600;cursor:pointer">下载视频</button></a>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("重新生成",key="gen_restart"):
                        for k in _defaults:
                            if k in st.session_state: del st.session_state[k]
                        st.rerun()
                with c2:
                    if st.button("换风格重新生成", key="gen_restyle"):
                        st.session_state.quick_mode_step = "style"
                        st.session_state.quick_mode_prompt = ""
                        st.session_state.quick_mode_final_prompt = ""
                        st.session_state.quick_gen_task_id = None
                        if "quick_mode_duration" in st.session_state: st.session_state.quick_mode_duration = 8
                        st.rerun()
                with c3:
                    if st.button("修改创意项", key="gen_reidea"):
                        st.session_state.quick_mode_step = "input"
                        st.session_state.quick_mode_ideas = []
                        st.session_state.quick_mode_prompt = ""
                        st.session_state.quick_gen_task_id = None
                        st.rerun()
            elif state < 0:
                st.error("生成失败: "+(task.get("error") or task.get("message") or "未知错误"))
                if st.button("返回修改"): st.session_state.quick_mode_step="prompt"; st.rerun()
            else:
                time.sleep(3); st.rerun()
        except Exception as e: st.error("查询状态失败: "+str(e))
        st.divider()
