from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY, logger
from core.state import AgentState
from typing import Annotated


def reviewer_node(state: Annotated[dict, AgentState]) -> dict:
    """审稿人智能体：检查文章质量"""
    logger.info("审稿人启动")
    draft = state.get("draft", "")
    question = state.get("question", "")

    if not draft:
        logs = state.get("logs", [])
        logs.append("[审稿人] 没有草稿")
        logger.info("审稿人完成（无草稿）")
        return {
            "review_feedback": ["没有可审阅的草稿。"],
            "logs": logs,
            "current_agent": "reviewer"
        }

    prompt = f"""你是一名严格的编辑。请针对以下文章进行审阅，原始问题为：{question}

文章草稿：
{draft}

请从以下方面检查：
1. 准确性：是否存在事实错误或逻辑漏洞？
2. 结构：章节安排是否清晰合理？
3. 语言：是否存在冗余或生硬的表述？
4. 完整性：是否回答了原问题？

输出要求：
- 给出 3-5 条具体建议，每条建议需包含“问题”和“解决方案”；
- 最后给出总体评价（优秀/良好/需改进）。

请用中文输出，内容具体、有建设性。"""

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        base_url=OPENAI_BASE_URL,
        temperature=0.3,
        api_key=OPENAI_API_KEY
    )
    response = llm.invoke(prompt)

    # 将返回内容按行分割，过滤空行，作为反馈列表
    review_feedback = [fb.strip() for fb in response.content.split(chr(10)) if fb.strip()]

    logs = state.get("logs", [])
    logs.append(f"[审稿人] 完成，共 {len(review_feedback)} 条建议")
    logger.info("审稿人完成")

    return {
        "review_feedback": review_feedback,
        "logs": logs,
        "current_agent": "reviewer"
    }