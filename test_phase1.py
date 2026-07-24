import sys, os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- {detail}")

# ============================================================
# 1.1 目录结构
# ============================================================
print("=" * 50)
print("1.1 目录结构")
print("=" * 50)
check("prompts/skills/ 目录存在", os.path.isdir("prompts/skills"))
check("config/ 目录存在", os.path.isdir("config"))
check("storage/ 目录存在", os.path.isdir("storage"))

# ============================================================
# 1.2 config/app.yaml
# ============================================================
print()
print("=" * 50)
print("1.2 config/app.yaml")
print("=" * 50)
check("app.yaml 文件存在", os.path.isfile("config/app.yaml"))
if os.path.isfile("config/app.yaml"):
    try:
        import yaml
        with open("config/app.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        check("features 节点存在", "features" in cfg)
        check("agent_enabled=false", cfg.get("features", {}).get("agent_enabled") == False)
        check("sqlite_enabled=false", cfg.get("features", {}).get("sqlite_enabled") == False)
        check("skill_system_enabled=false", cfg.get("features", {}).get("skill_system_enabled") == False)
        check("database.path 存在", "database" in cfg and "path" in cfg["database"])
        check("agent.max_steps=5", cfg.get("agent", {}).get("max_steps") == 5)
        check("evaluation.min_time_slices=4", cfg.get("evaluation", {}).get("min_time_slices") == 4)
    except Exception as e:
        check("app.yaml 解析", False, str(e))

# ============================================================
# 1.3 database.py
# ============================================================
print()
print("=" * 50)
print("1.3 database.py (SQLite)")
print("=" * 50)
from app.services import database
try:
    database.init_db()
    check("init_db() 不抛异常", True)
    
    # 检查表是否存在
    conn = database.get_connection()
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    check("tasks 表存在", "tasks" in tables)
    check("creative_cases 表存在", "creative_cases" in tables)
    check("agent_logs 表存在", "agent_logs" in tables)
    
    # save_task
    tid = "verify-" + str(os.getpid())
    database.save_task({"id": tid, "user_input": "验证测试", "style": "写实", "status": "done"})
    task = database.get_task(tid)
    check("save_task + get_task", task is not None and task["user_input"] == "验证测试")
    
    # list_tasks
    tasks = database.list_tasks(limit=5)
    check("list_tasks 返回结果", len(tasks) > 0)
    
    # save_creative_case + get_relevant_cases
    database.save_creative_case({"title": "测试案例", "description": "验证用", "keywords": "验证,测试", "quality_score": 0.8})
    cases = database.get_relevant_cases("验证")
    check("save_creative_case + get_relevant_cases", len(cases) > 0)
    
    # save_agent_log
    database.save_agent_log(tid, 1, "test_tool", "input_data", "output_data")
    check("save_agent_log 不抛异常", True)
    
except Exception as e:
    check("database 模块", False, str(e))

# ============================================================
# 1.4 skill_manager.py + 模板
# ============================================================
print()
print("=" * 50)
print("1.4 skill_manager.py + 模板")
print("=" * 50)
from app.services import skill_manager
try:
    skills = skill_manager.list_skills()
    check("list_skills 返回非空", len(skills) > 0)
    check("creative_ideas 模板存在", "creative_ideas" in skills)
    check("video_prompt 模板存在", "video_prompt" in skills)
    
    # load
    t1 = skill_manager.load_skill("creative_ideas")
    check("load creative_ideas", len(t1) > 100)
    t2 = skill_manager.load_skill("video_prompt")
    check("load video_prompt", len(t2) > 100)
    
    # render
    r1 = skill_manager.render_skill("creative_ideas", activity_theme="电信测试", extra_context="")
    check("render creative_ideas 含填充值", "电信测试" in r1)
    r2 = skill_manager.render_skill("video_prompt", activity_theme="测试", video_script="测试脚本", 
                                     style="写实", duration=8, min_slices=4, min_length=300,
                                     reference_rule="", camera_rule="固定机位")
    check("render video_prompt 含填充值", "测试" in r2 and "8秒" in r2)
except Exception as e:
    check("skill_manager 模块", False, str(e))

# ============================================================
# 1.5 tools.py
# ============================================================
print()
print("=" * 50)
print("1.5 tools.py (Agent 工具集)")
print("=" * 50)
from app.services import tools
try:
    check("TOOL_DEFINITIONS 有 3 个工具", len(tools.TOOL_DEFINITIONS) == 3)
    check("TOOL_HANDLERS 有 3 个处理器", len(tools.TOOL_HANDLERS) == 3)
    
    r = tools.evaluate_prompt_quality("坏的prompt")
    check("evaluate bad prompt: passed=False", r["passed"] == False)
    check("evaluate bad prompt: 有 issues", len(r["issues"]) > 0)
    
    good = "场景描述：明亮的电信营业厅。0.0-2.0秒：人物微笑进门。2.0-4.0秒：介绍套餐。4.0-6.0秒：展示手机。6.0-8.0秒：挥手告别。9:16竖屏，高清，画面稳定，无肢体畸形。" + "补充细节" * 60
    r2 = tools.evaluate_prompt_quality(good)
    check("evaluate good prompt: passed=True", r2["passed"] == True)
    check("evaluate good prompt: score接近1", r2["score"] > 0.9)
except Exception as e:
    check("tools 模块", False, str(e))

# ============================================================
# 总结
# ============================================================
print()
print("=" * 50)
print(f"结果: {passed} 通过, {failed} 失败, 共 {passed+failed} 项")
print("=" * 50)
if failed > 0:
    sys.exit(1)
