"""
测试：数据库、评测器、工具集
"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class TestDatabase:
    def test_init_db(self):
        from app.services import database
        database.init_db()
        assert True

    def test_save_and_get_task(self):
        from app.services import database
        database.init_db()
        tid = "pytest-" + str(hash("test_save"))
        database.save_task({
            "id": tid,
            "user_input": "测试活动",
            "style": "写实",
            "duration": 8,
            "prompt": "测试提示词",
            "final_prompt": "最终提示词",
            "status": "completed",
            "video_urls": ["http://127.0.0.1:8080/tasks/test/final-1.mp4"],
        })
        task = database.get_task(tid)
        assert task is not None
        assert task["user_input"] == "测试活动"
        assert task["style"] == "写实"
        td = task.get("task_data", {})
        if isinstance(td, str):
            import json; td = json.loads(td)
        urls = td.get("video_urls", [])
        assert len(urls) == 1

    def test_list_tasks(self):
        from app.services import database
        database.init_db()
        tasks = database.list_tasks(limit=5)
        assert isinstance(tasks, list)

    def test_creative_cases(self):
        from app.services import database
        database.init_db()
        database.save_creative_case({
            "title": "测试案例",
            "description": "这是一个测试",
            "keywords": "测试,单元测试",
            "quality_score": 0.8,
        })
        cases = database.get_relevant_cases("测试")
        assert len(cases) > 0


class TestEvaluator:
    def test_bad_prompt(self):
        from app.services import evaluator
        r = evaluator.evaluate_prompt_quality("坏的提示词")
        assert r["passed"] is False
        assert len(r["issues"]) > 0

    def test_good_prompt(self):
        from app.services import evaluator
        prompt = (
            "场景总描述：明亮的电信营业厅。"
            "0.0-2.0秒：人物微笑进门，表情自然。"
            "2.0-4.0秒：介绍产品套餐，口型清晰。"
            "4.0-6.0秒：展示手机特写，动作流畅。"
            "6.0-8.0秒：用户惊喜表情，握手致谢。"
            "9:16竖屏，高清，画面稳定，无肢体畸形。"
            + "补充细节确保画质优秀背景一致。"
            * 12
        )
        r = evaluator.evaluate_prompt_quality(prompt)
        assert r["passed"] is True
        assert r["score"] >= 0.9

    def test_bad_creative_ideas(self):
        from app.services import evaluator
        ideas = [
            {"title": "t1", "description": "d1", "style": "warm"},
            {"title": "t2", "description": "d2", "style": "warm"},
        ]
        r = evaluator.evaluate_creative_ideas(ideas)
        assert r["passed"] is False

    def test_good_creative_ideas(self):
        from app.services import evaluator
        ideas = [
            {"title": "方案1", "description": "描述内容" * 5, "style": "warm"},
            {"title": "方案2", "description": "描述内容" * 5, "style": "humor"},
            {"title": "方案3", "description": "描述内容" * 5, "style": "direct"},
            {"title": "方案4", "description": "描述内容" * 5, "style": "suspense"},
            {"title": "方案5", "description": "描述内容" * 5, "style": "scenic"},
            {"title": "方案6", "description": "描述内容" * 5, "style": "social"},
        ]
        r = evaluator.evaluate_creative_ideas(ideas)
        assert r["passed"] is True


class TestTools:
    def test_search_cases(self):
        from app.services import tools
        r = tools.search_relevant_cases("测试")
        assert r["success"] is True

    def test_evaluate_prompt(self):
        from app.services import tools
        r = tools.evaluate_prompt_quality("坏的提示词", min_slices=4, min_length=300)
        assert r["success"] is True
        assert r["passed"] is False

    def test_tool_definitions(self):
        from app.services import tools
        assert len(tools.TOOL_DEFINITIONS) == 10
        assert len(tools.TOOL_HANDLERS) == 10
        assert "search_relevant_cases" in tools.TOOL_HANDLERS
        assert "evaluate_prompt_quality" in tools.TOOL_HANDLERS
        assert "evaluate_creative_ideas" in tools.TOOL_HANDLERS


class TestSkillManager:
    def test_list_skills(self):
        from app.services import skill_manager
        skills = skill_manager.list_skills()
        assert "creative_ideas" in skills
        assert "video_prompt" in skills

    def test_render_skill(self):
        from app.services import skill_manager
        r = skill_manager.render_skill("creative_ideas", activity_theme="测试", extra_context="")
        assert "测试" in r

class TestAgent:
    def test_agent_no_tools(self):
        from app.services import agent
        result = agent.run_agent(
            system_prompt="You are a helpful assistant.",
            user_message="Say hello.",
            tools=[],
            tool_handlers={},
            max_steps=2,
        )
        assert result["success"] is True
        assert len(result["answer"]) > 0

    def test_agent_with_tools(self):
        from app.services import agent
        from app.services.tools import TOOL_DEFINITIONS, TOOL_HANDLERS
        result = agent.run_agent(
            system_prompt="Search for creative cases using search_relevant_cases, then tell me the result.",
            user_message="Keywords: telecom",
            tools=TOOL_DEFINITIONS,
            tool_handlers=TOOL_HANDLERS,
            max_steps=3,
        )
        assert result["success"] is True
        assert len(result["steps"]) > 0

class TestJudge:
    def test_judge_import(self):
        from app.services import judge
        assert hasattr(judge, 'judge_creative_ideas')
        assert hasattr(judge, 'run_full_evaluation')

    def test_guard_import(self):
        from app.services import guard
        r = guard.check_safety("Normal safe content")
        assert r["success"] is True

    def test_guard_sensitive(self):
        from app.services import guard
        r = guard.check_safety("This is the best product, 100% guaranteed!")
        assert len(r["issues"]) > 0
