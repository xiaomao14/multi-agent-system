"""
修订写手智能体：根据审稿意见修改文章
"""

from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY, logger
from core.state import AgentState
from typing import Annotated


def reviser_node(state: Annotated[dict, AgentState]) -> dict:
    """修订写手智能体：根据审稿意见修改文章"""
    logger.info("修订写手启动")

    draft = state.get("draft", "")
    review_feedback = state.get("review_feedback", [])
    question = state.get("question", "")

    # 如果没有草稿或没有审稿意见，直接返回初稿
    if not draft:
        logs = state.get("logs", [])
        logs.append("[修订写手] 没有草稿可修订")
        logger.info("修订写手完成（无草稿）")
        return {
            "final_article": "没有可修订的草稿。",
            "logs": logs,
            "current_agent": "reviser"
        }

    if not review_feedback:
        logs = state.get("logs", [])
        logs.append("[修订写手] 没有审稿意见，直接使用初稿")
        logger.info("修订写手完成（无审稿意见）")
        return {
            "final_article": draft,
            "logs": logs,
            "current_agent": "reviser"
        }

    # 将审稿意见拼接成字符串
    feedback_text = "\n".join([f"- {fb}" for fb in review_feedback])

    prompt = f"""你是一个专业的文章修订编辑。请根据以下审稿意见，对文章进行修改和完善。

原始问题：{question}

文章初稿：
{draft}

审稿意见：
{feedback_text}

修改要求：
1. 逐条回应审稿意见，对文章进行针对性修改
2. 保留原文的优点和正确内容，只修改有问题部分
3. 确保全文逻辑连贯、语言流畅
4. 修改后输出完整文章（不是只输出修改部分）
5. 在文章最后，用"【修改说明】"标题列出你做了哪些具体修改

请直接输出修改后的完整文章。"""

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        base_url=OPENAI_BASE_URL,
        temperature=0.5,
        api_key=OPENAI_API_KEY
    )
    response = llm.invoke(prompt)

    logs = state.get("logs", [])
    logs.append(f"[修订写手] 修订完成，共 {len(response.content)} 字符")
    logger.info("修订写手完成")

    return {
        "final_article": response.content,
        "logs": logs,
        "current_agent": "reviser"
    }