"""
FinalEditor 节点：终审编辑
根据审稿意见和人工审核意见，生成最终文章。
"""

from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY, logger
from core.state import AgentState
from typing import Annotated


def final_editor_node(state: Annotated[dict, AgentState]) -> dict:
    """
    终审编辑节点
    
    职责：
    1. 如果人工审核通过 → 直接基于审稿意见修订
    2. 如果人工审核拒绝 → 结合用户自定义意见重新修订
    """
    logger.info("终审编辑启动")

    draft = state.get("draft", "")
    review_feedback = state.get("review_feedback", [])
    human_status = state.get("human_review_status", "pending")
    human_comment = state.get("human_review_comment", "")
    question = state.get("question", "")
    logs = state.get("logs", [])

    # 如果没有草稿，直接返回
    if not draft:
        logs.append("[终审编辑] 没有草稿可修订")
        logger.info("终审编辑完成（无草稿）")
        return {
            "final_article": "没有可修订的草稿。",
            "logs": logs,
            "current_agent": "final_editor"
        }

    # 构建审稿意见文本
    ai_feedback_text = ""
    if review_feedback:
        ai_feedback_text = "\n".join([f"- {fb}" for fb in review_feedback])

    # 构建 Prompt
    if human_status == "rejected" and human_comment:
        # 用户拒绝了，且有自定义意见
        prompt = f"""你是一个专业的文章终审编辑。请根据以下所有意见对文章进行全面修改。

原始问题：{question}

文章初稿：
{draft}

AI 审稿意见：
{ai_feedback_text if ai_feedback_text else "无"}

人工审核意见（用户明确要求修改）：
{human_comment}

修改要求：
1. 必须逐条回应 AI 审稿意见和人工审核意见
2. 人工审核意见优先级高于 AI 审稿意见
3. 保留原文的优点和正确内容，只修改有问题部分
4. 确保全文逻辑连贯、语言流畅
5. 修改后输出完整文章（不是只输出修改部分）
6. 在文章最后，用"【修改说明】"标题列出你做了哪些具体修改

请直接输出修改后的完整文章。"""
    elif human_status == "approved":
        # 用户通过了，正常修订
        prompt = f"""你是一个专业的文章终审编辑。请根据以下审稿意见对文章进行修改和完善。

原始问题：{question}

文章初稿：
{draft}

审稿意见：
{ai_feedback_text if ai_feedback_text else "无"}

修改要求：
1. 逐条回应审稿意见，对文章进行针对性修改
2. 保留原文的优点和正确内容，只修改有问题部分
3. 确保全文逻辑连贯、语言流畅
4. 修改后输出完整文章（不是只输出修改部分）
5. 在文章最后，用"【修改说明】"标题列出你做了哪些具体修改

请直接输出修改后的完整文章。"""
    else:
        # 没有审稿意见，直接返回初稿
        logs.append("[终审编辑] 没有审稿意见，直接使用初稿")
        logger.info("终审编辑完成（无审稿意见）")
        return {
            "final_article": draft,
            "logs": logs,
            "current_agent": "final_editor"
        }

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        base_url=OPENAI_BASE_URL,
        temperature=0.5,
        api_key=OPENAI_API_KEY
    )
    response = llm.invoke(prompt)

    logs.append(f"[终审编辑] 修订完成，共 {len(response.content)} 字符")
    logger.info("终审编辑完成")

    return {
        "final_article": response.content,
        "logs": logs,
        "current_agent": "final_editor",
        "current_stage": "finalized"
    }