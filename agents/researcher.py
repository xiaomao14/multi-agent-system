"""
研究员智能体：收集和整理资料
"""

from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY, logger
from core.state import AgentState
from typing import Annotated


def researcher_node(state: Annotated[dict, AgentState]) -> dict:
    """研究员智能体：根据规划者的计划收集资料"""
    logger.info("[节点日志] 研究员启动")

    question = state.get("question", "")
    plan = state.get("plan", {})
    research_tasks = plan.get("research_tasks", [])
    logs = state.get("logs", [])

    # 如果有具体任务计划，优先使用；否则用原始问题
    if research_tasks:
        task_summary = "，".join(research_tasks)
        prompt = f"""你是一个专业的研究员。请针对以下调研方向收集资料：

研究问题：{question}
主题：{plan.get('topic', question)}

调研方向：
{chr(10).join([f'{i+1}. {task}' for i, task in enumerate(research_tasks)])}

请按以下格式输出：
1. 关键概念（3-5个）
2. 重要数据和事实
3. 相关案例或例子
4. 不同观点

要求：准确、简洁、有条理。"""
    else:
        prompt = f"""你是一个专业的研究员。请收集以下问题的资料：

{question}

请按以下格式输出：
1. 关键概念（3-5个）
2. 重要数据和事实
3. 相关案例或例子
4. 不同观点

要求：准确、简洁、有条理。"""

    try:
        llm = ChatOpenAI(
            model=OPENAI_MODEL,
            base_url=OPENAI_BASE_URL,
            temperature=0.3,
            api_key=OPENAI_API_KEY
        )
        response = llm.invoke(prompt)
        research_data = [response.content]

        logs.append(f"[研究员] 完成，收集 {len(research_data)} 份资料")
        logger.info("[节点日志] 研究员完成 - 输入: {question[:30]}, 输出: {len(research_data)} 份资料".format(question=question))

        return {
            "research_data": research_data,
            "logs": logs,
            "current_agent": "researcher",
            "current_stage": "research",
            "agent_results": state.get("agent_results", []) + [{"agent": "researcher", "status": "completed"}]
        }

    except Exception as e:
        logger.error(f"研究员异常: {e}")
        logs.append(f"[研究员] 异常: {str(e)}")
        return {
            "research_data": [],
            "logs": logs,
            "current_agent": "researcher",
            "current_stage": "research",
            "agent_results": state.get("agent_results", []) + [{"agent": "researcher", "status": "error"}]
        }