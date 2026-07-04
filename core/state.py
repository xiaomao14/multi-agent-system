from typing import TypedDict, Annotated
import operator


class AgentState(TypedDict):
    """Agent collaboration state"""
    question: str
    research_data: list
    analysis_report: str
    draft: str
    review_feedback: list
    final_article: str
    logs: Annotated[list, operator.add]
    current_agent: str
