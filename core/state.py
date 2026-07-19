from typing import TypedDict, Annotated
import operator


class AgentState(TypedDict):
    '''Agent collaboration state'''
    question: str
    plan: dict
    current_stage: str
    agent_results: list
    research_data: list
    analysis_report: str
    draft: str
    review_feedback: list
    human_review_status: str          # pending / approved / rejected / edited
    human_review_comment: str          # 用户自定义修改意见
    final_article: str
    logs: Annotated[list, operator.add]
    current_agent: str