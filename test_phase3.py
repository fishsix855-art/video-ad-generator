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

print("=" * 50)
print("Phase 3: agent.py")
print("=" * 50)
from app.services import agent
check("agent module imported", True)
check("MAX_STEPS defined", hasattr(agent, 'MAX_STEPS'))
check("run_agent function exists", hasattr(agent, 'run_agent'))

print()
print("=" * 50)
print("Phase 3: evaluator.py")
print("=" * 50)
from app.services import evaluator

r = evaluator.evaluate_prompt_quality("bad prompt")
check("evaluate bad prompt: passed=False", r["passed"] == False)
check("evaluate bad prompt: has issues", len(r["issues"]) > 0)

# Build a truly good prompt with 300+ chars
good = "场景总描述：明亮干净的电信营业厅大厅，阳光透过玻璃窗洒在地面。0.0-2.0秒：一位微笑的营业员从柜台后走出，向镜头挥手致意。2.0-4.0秒：营业员拿出手机展示最新5G套餐，表情自信专业。4.0-6.0秒：镜头切换到用户惊喜的表情，手中拿着优惠券。6.0-8.0秒：营业员与用户握手，画面定格在两人满意的笑容。9:16竖屏，高清，画面稳定，动作自然流畅，无肢体畸形，无多余杂乱文字，背景保持一致，写实商业广告风格。"
r2 = evaluator.evaluate_prompt_quality(good)
check("evaluate good prompt: passed=True", r2["passed"] == True)
check("evaluate good prompt: score > 0.9", r2["score"] > 0.9)

r3 = evaluator.evaluate_creative_ideas([
    {"title": "温情篇", "description": "一个温暖的家庭故事，展现电信套餐带来的连接与关怀。" * 2, "style": "warm"},
    {"title": "幽默篇", "description": "搞笑的营业厅故事，用夸张手法展示优惠力度与趣味性。" * 2, "style": "humor"},
    {"title": "直给篇", "description": "快节奏展示数字优惠，突出限时折扣与性价比。" * 2, "style": "direct"},
    {"title": "悬念篇", "description": "开头设置悬念，反转揭示超值套餐的惊喜。" * 2, "style": "suspense"},
    {"title": "场景篇", "description": "日常生活中的温馨场景，自然融入电信服务。" * 2, "style": "scenic"},
    {"title": "口碑篇", "description": "用户真实分享，大量好评展示服务质量与口碑。" * 2, "style": "social"},
])
check("evaluate good ideas: passed=True", r3["passed"] == True)
check("evaluate good ideas: 6 unique styles", len(r3["details"]["style_duplicates"]) == 0)

print()
print("=" * 50)
print("Phase 3: llm.py agent functions")
print("=" * 50)
from app.services import llm
check("generate_creative_ideas_with_agent exists", hasattr(llm, 'generate_creative_ideas_with_agent'))
check("generate_video_prompt_with_agent exists", hasattr(llm, 'generate_video_prompt_with_agent'))

print()
print("=" * 50)
print("Phase 3: feature flags")
print("=" * 50)
import yaml
with open("config/app.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
check("agent_enabled is False", cfg["features"]["agent_enabled"] == False)

print()
print("=" * 50)
print(f"Result: {passed} passed, {failed} failed, total {passed+failed}")
print("=" * 50)
if failed > 0:
    sys.exit(1)