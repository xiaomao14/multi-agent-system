"""
工作流编排 - 支持 Human-in-the-Loop 审核
使用 LangGraph 将多个智能体串联成完整流程
"""

from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.planner_agent import planner_node
from agents.researcher import researcher_node
from agents.analyst import analyst_node
from agents.writer import writer_node
from agents.reviewer import reviewer_node
from agents.human_review import human_review_node
from agents.final_editor import final_editor_node
from core.filter_nodes import filter_research_node
from core.config import logger
from core.memory import get_memory_manager

_app = None


def build_graph():
    """构建智能体协作工作流图"""
    logger.info("开始构建工作流图...")

    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("filter", filter_research_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("final_editor", final_editor_node)

    # 设置入口点
    workflow.set_entry_point("planner")

    # 定义执行顺序：
    # 规划者 -> 研究员 -> 过滤器 -> 分析师 -> 写手 -> 审稿人 -> 人工审核 -> 终审编辑 -> 结束
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "filter")
    workflow.add_edge("filter", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", "reviewer")
    workflow.add_edge("reviewer", "human_review")

    # 条件路由：根据人工审核结果决定下一步
    def route_after_human_review(state):
        """根据人工审核状态路由到不同节点"""
        review_status = state.get("human_review_status", "pending")
        if review_status == "approved":
            return "final_editor"
        elif review_status == "rejected":
            return "final_editor"  # 终审编辑会读取 human_review_comment
        else:
            return "final_editor"

    workflow.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "final_editor": "final_editor",
        }
    )

    workflow.add_edge("final_editor", END)

    app = workflow.compile()
    logger.info("工作流图构建成功")
    return app


def get_app():
    """获取编译好的工作流应用（单例模式）"""
    global _app
    if _app is None:
        _app = build_graph()
    return _app


def run_workflow(
    question: str,
    session_id: str = None,
    continue_from_task: dict = None,
    human_decision: str = "approved",
    human_comment: str = ""
) -> dict:
    """
    运行完整的工作流

    Args:
        question: 用户研究问题
        session_id: 会话ID（用于记忆和历史追踪）
        continue_from_task: 如果提供，基于上一个任务的结果继续修改
        human_decision: 人工审核决策 ("approved" / "rejected")
        human_comment: 人工审核时的自定义修改意见

    Returns:
        包含最终结果的字典
    """
    logger.info(f"开始运行工作流，问题: {question}")

    # 获取或创建 session
    if not session_id:
        session_id = get_memory_manager().create_session()

    # 初始化状态
    initial_state = {
        "question": question,
        "plan": {},
        "current_stage": "",
        "agent_results": [],
        "research_data": [],
        "analysis_report": "",
        "draft": "",
        "review_feedback": [],
        "human_review_status": human_decision,
        "human_review_comment": human_comment,
        "final_article": "",
        "logs": [],
        "current_agent": ""
    }

    # 如果是基于历史任务继续修改，注入上下文
    if continue_from_task:
        topic = continue_from_task.get("topic", "N/A")
        logger.info(f"基于历史任务继续修改: {topic}")
        initial_state["draft"] = continue_from_task.get(
            "final_article", continue_from_task.get("draft", "")
        )
        initial_state["review_feedback"] = continue_from_task.get("review_feedback", [])
        initial_state["logs"].append(
            f"[系统] 基于历史任务继续修改，上一任务: {topic}"
        )
        prev_len = len(initial_state.get("draft", "0"))
        initial_state["logs"].append(
            f"[系统] 上一篇文章长度: {prev_len} 字符"
        )

    app = get_app()

    try:
        result = app.invoke(initial_state)

        # 保存结果到 memory
        task_id = get_memory_manager().save_task(session_id, result, question)
        logger.info(f"任务已保存到 memory: {task_id}")

        # 附加元数据
        result["task_id"] = task_id
        result["session_id"] = session_id

        logger.info("工作流运行完成")
        return result

    except Exception as e:
        logger.error(f"工作流运行失败: {e}", exc_info=True)
        get_memory_manager().save_failed_task(session_id, question, str(e))
        raise