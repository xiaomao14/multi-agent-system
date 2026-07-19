import json
import sqlite3
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.config import logger


class MemoryManager:
    """
    会话记忆管理器
    
    功能：
    - 使用 SQLite 持久化存储每次任务的完整结果
    - 为每个会话分配唯一 session_id
    - 支持查看历史任务列表
    - 支持基于历史结果继续修改文章
    - 不改变已有 Agent 接口
    """
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "memory.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                topic TEXT,
                plan_json TEXT,
                draft TEXT,
                final_article TEXT,
                review_feedback_json TEXT,
                logs_json TEXT,
                status TEXT DEFAULT 'completed',
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_session ON tasks(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_question ON tasks(question)")
        
        conn.commit()
        conn.close()
        logger.info(f"Memory database initialized: {self.db_path}")
    
    def create_session(self, name=None):
        """创建新会话，返回 session_id"""
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (session_id, name or session_id, now, now)
        )
        conn.commit()
        conn.close()
        
        logger.info(f"Session created: {session_id}")
        return session_id
    
    def save_task(self, session_id, result, question):
        """保存任务结果到数据库，返回 task_id"""
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        plan = result.get("plan", {})
        feedback = result.get("review_feedback", [])
        logs = result.get("logs", [])
        
        topic = plan.get("topic", "") if isinstance(plan, dict) else ""
        plan_json = json.dumps(plan, ensure_ascii=False) if isinstance(plan, dict) else ""
        feedback_json = json.dumps(feedback, ensure_ascii=False) if isinstance(feedback, list) else ""
        logs_json = json.dumps(logs, ensure_ascii=False) if isinstance(logs, list) else ""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks 
            (id, session_id, question, topic, plan_json, draft, final_article,
             review_feedback_json, logs_json, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id, session_id, question, topic,
            plan_json, result.get("draft", ""), result.get("final_article", ""),
            feedback_json, logs_json, "completed", now, now
        ))
        conn.commit()
        
        cursor.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
        conn.commit()
        conn.close()
        
        logger.info(f"Task saved: {task_id} in session {session_id}")
        return task_id
    
    def save_failed_task(self, session_id, question, error):
        """保存失败的任务记录"""
        task_id = f"task_fail_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (id, session_id, question, status, error_message, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (task_id, session_id, question, "failed", error, now, now)
        )
        conn.commit()
        conn.close()
        
        logger.warning(f"Failed task saved: {task_id}")
        return task_id
    
    def get_task(self, task_id):
        """获取单个任务详情"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def get_session_history(self, session_id, limit=50):
        """获取某个会话的历史任务列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_all_sessions(self):
        """获取所有会话列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.name, s.created_at, s.updated_at,
                   COUNT(t.id) as task_count,
                   MAX(t.created_at) as last_task_time
            FROM sessions s
            LEFT JOIN tasks t ON s.id = t.session_id
            GROUP BY s.id
            ORDER BY s.updated_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def _row_to_dict(self, row):
        """将数据库行转换为字典，自动解析 JSON 字段"""
        d = dict(row)
        
        for json_field in ["plan_json", "review_feedback_json", "logs_json"]:
            key = json_field.replace("_json", "")
            if json_field in d and d[json_field]:
                try:
                    d[key] = json.loads(d[json_field])
                except (json.JSONDecodeError, TypeError):
                    d[key] = []
        
        return d
    
    def delete_task(self, task_id):
        """删除任务记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def delete_session(self, session_id):
        """删除会话及其所有任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted


# 全局单例
_memory_manager = None


def get_memory_manager():
    """获取全局 MemoryManager 单例"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager