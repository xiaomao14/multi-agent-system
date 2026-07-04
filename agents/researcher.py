from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY, logger
from core.state import AgentState
from typing import Annotated


def researcher_node(state: Annotated[dict, AgentState]) -> dict:
    """研究员智能体：收集和整理信息"""
    logger.info("研究员启动")
    question = state.get("question", "")

    prompt = f"""你是一名专业的研究员。请为以下问题收集和整理相关资料：{question}

输出格式（请严格按照以下结构）：
1. 核心概念（3-5个）
2. 重要数据和事实
3. 相关案例或实例
4. 不同角度的观点

要求：内容准确、简洁、结构清晰。"""

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        base_url=OPENAI_BASE_URL,
        temperature=0.3,
        api_key=OPENAI_API_KEY
    )
    response = llm.invoke(prompt)
    research_data = [response.content]

    logs = state.get("logs", [])
    logs.append(f"[研究员] 完成，共 {len(research_data)} 条资料")

    logger.info("研究员完成")
    return {
        "research_data": research_data,
        "logs": logs,
        "current_agent": "researcher"
    }
