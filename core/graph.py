"""
工作流编排
使用 LangGraph 将多个智能体串联成完整流程
"""

from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.researcher import researcher_node
from agents.analyst import analyst_node
from agents.writer import writer_node
from agents.reviewer import reviewer_node
from agents.reviser import reviser_node
from core.filter_nodes import filter_research_node
from core.config import logger

# 缓存编译后的图，避免每次调用都重新编译
_app = None


def build_graph():
    """构建智能体协作工作流图"""
    logger.info("开始构建工作流图...")

    workflow = StateGraph(AgentState)

    # 添加 6 个节点
    workflow.add_node("researcher", researcher_node)     # 研究员：收集资料
    workflow.add_node("filter", filter_research_node)     # 过滤器：质量把关
    workflow.add_node("analyst", analyst_node)            # 分析师：分析资料
    workflow.add_node("writer", writer_node)              # 写手：撰写初稿
    workflow.add_node("reviewer", reviewer_node)          # 审稿人：审查质量
    workflow.add_node("reviser", reviser_node)            # 修订写手：根据意见修改

    # 设置入口点
    workflow.set_entry_point("researcher")

    # 定义执行顺序：
    # 研究员 → 过滤器 → 分析师 → 写手 → 审稿人 → 修订写手 → 结束
    workflow.add_edge("researcher", "filter")
    workflow.add_edge("filter", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", "reviewer")
    workflow.add_edge("reviewer", "reviser")
    workflow.add_edge("reviser", END)

    app = workflow.compile()
    logger.info("工作流图构建成功")
    return app


def get_app():
    """获取编译好的工作流应用（单例模式，避免重复编译）"""
    global _app
    if _app is None:
        _app = build_graph()
    return _app


def run_workflow(question: str) -> dict:
    """运行完整的工作流"""
    logger.info(f"开始运行工作流，问题: {question}")

    initial_state = {
        "question": question,
        "research_data": [],
        "analysis_report": "",
        "draft": "",
        "review_feedback": [],
        "final_article": "",
        "logs": [],
        "current_agent": ""
    }

    app = get_app()
    result = app.invoke(initial_state)

    logger.info("工作流运行完成")
    return result