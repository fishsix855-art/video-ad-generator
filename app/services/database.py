'''
SQLite 数据库模块 - 存储任务记录和历史创意案例
使用 Python 标准库 sqlite3，无需额外安装
'''
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

DB_PATH = "storage/tasks.db"


def get_db_path():
    '''获取数据库文件路径，自动创建父目录'''
    root = Path(__file__).parent.parent.parent
    db_path = root / DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return str(db_path)


def get_connection():
    '''获取数据库连接，自动开启 WAL 模式提高并发性能'''
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    '''初始化数据库表结构，幂等操作'''
    conn = get_connection()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            user_input TEXT NOT NULL,
            creative_idea TEXT,
            style TEXT,
            duration INTEGER DEFAULT 8,
            prompt TEXT,
            final_prompt TEXT,
            status TEXT DEFAULT 'pending',
            task_data TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS creative_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            style TEXT,
            prompt TEXT,
            keywords TEXT,
            quality_score REAL DEFAULT 0.5,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            step_number INTEGER,
            tool_name TEXT,
            input_data TEXT,
            output_data TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);
        CREATE INDEX IF NOT EXISTS idx_cases_keywords ON creative_cases(keywords);
        CREATE INDEX IF NOT EXISTS idx_agent_logs_task ON agent_logs(task_id);
    ''')
    conn.commit()
    conn.close()


def save_task(task_data: dict):
    '''保存或更新任务记录'''
    conn = get_connection()
    task_id = task_data.get("id", "")
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    existing = conn.execute("SELECT id FROM tasks WHERE id=?", (task_id,)).fetchone()
    if existing:
        conn.execute('''
            UPDATE tasks SET user_input=?, creative_idea=?, style=?, duration=?,
            prompt=?, final_prompt=?, status=?, task_data=?, updated_at=?
            WHERE id=?
        ''', (
            task_data.get("user_input", ""),
            json.dumps(task_data.get("creative_idea", {}), ensure_ascii=False),
            task_data.get("style", ""),
            task_data.get("duration", 8),
            task_data.get("prompt", ""),
            task_data.get("final_prompt", ""),
            task_data.get("status", "pending"),
            json.dumps(task_data, ensure_ascii=False),
            now,
            task_id,
        ))
    else:
        conn.execute('''
            INSERT INTO tasks (id, user_input, creative_idea, style, duration, prompt, final_prompt, status, task_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            task_data.get("user_input", ""),
            json.dumps(task_data.get("creative_idea", {}), ensure_ascii=False),
            task_data.get("style", ""),
            task_data.get("duration", 8),
            task_data.get("prompt", ""),
            task_data.get("final_prompt", ""),
            task_data.get("status", "pending"),
            json.dumps(task_data, ensure_ascii=False),
        ))
    conn.commit()
    conn.close()


def get_task(task_id: str) -> dict | None:
    '''根据 ID 获取任务记录'''
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    task = dict(row)
    for field in ("creative_idea", "task_data"):
        if task.get(field):
            try:
                task[field] = json.loads(task[field])
            except json.JSONDecodeError:
                pass
    return task


def list_tasks(limit: int = 20, offset: int = 0) -> list[dict]:
    '''分页获取任务列表，按时间倒序'''
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, user_input, style, status, created_at FROM tasks ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_creative_case(case: dict):
    '''保存一个优秀创意案例到知识库'''
    conn = get_connection()
    conn.execute('''
        INSERT INTO creative_cases (title, description, style, prompt, keywords, quality_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        case.get("title", ""),
        case.get("description", ""),
        case.get("style", ""),
        case.get("prompt", ""),
        case.get("keywords", ""),
        case.get("quality_score", 0.5),
    ))
    conn.commit()
    conn.close()


def get_relevant_cases(keywords: str, limit: int = 3) -> list[dict]:
    '''根据关键词模糊检索相关创意案例'''
    conn = get_connection()
    search = f"%{keywords}%"
    rows = conn.execute(
        "SELECT title, description, style, prompt, quality_score FROM creative_cases WHERE keywords LIKE ? ORDER BY quality_score DESC LIMIT ?",
        (search, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_agent_log(task_id: str, step_number: int, tool_name: str, input_data: str, output_data: str):
    '''记录 Agent 每一步的推理过程'''
    conn = get_connection()
    conn.execute(
        "INSERT INTO agent_logs (task_id, step_number, tool_name, input_data, output_data) VALUES (?, ?, ?, ?, ?)",
        (task_id, step_number, tool_name, str(input_data)[:5000], str(output_data)[:5000])
    )
    conn.commit()
    conn.close()


init_db()
