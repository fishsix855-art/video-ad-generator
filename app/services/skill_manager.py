'''
Prompt 技能管理器 - 从 .txt 文件加载 Prompt 模板并填充变量
'''
import os
from pathlib import Path
from string import Template


def get_skills_dir():
    '''获取 prompts/skills 目录的绝对路径'''
    root = Path(__file__).parent.parent.parent
    return str(root / "prompts" / "skills")


def load_skill(skill_name: str) -> str:
    '''
    加载指定技能的 Prompt 模板
    
    Args:
        skill_name: 技能名称（不含 .txt 后缀），如 "creative_ideas" 或 "video_prompt"
    
    Returns:
        模板文本内容
    '''
    skills_dir = get_skills_dir()
    filepath = os.path.join(skills_dir, f"{skill_name}.txt")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Skill template not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def render_skill(skill_name: str, **variables) -> str:
    '''
    加载并填充技能模板
    
    Args:
        skill_name: 技能名称
        **variables: 模板变量，如 activity_theme="电信活动"
    
    Returns:
        填充后的完整 Prompt
    '''
    template = load_skill(skill_name)
    return Template(template).safe_substitute(**variables)


def list_skills() -> list[str]:
    '''列出所有可用的技能模板名称'''
    skills_dir = get_skills_dir()
    if not os.path.exists(skills_dir):
        return []
    return [f.replace(".txt", "") for f in os.listdir(skills_dir) if f.endswith(".txt")]


def save_skill(skill_name: str, content: str):
    '''保存或更新技能模板内容'''
    skills_dir = get_skills_dir()
    os.makedirs(skills_dir, exist_ok=True)
    filepath = os.path.join(skills_dir, f"{skill_name}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
