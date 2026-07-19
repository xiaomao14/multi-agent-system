"""
规划者智能体：分析用户需求，生成结构化任务计划
"""

from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY, logger
from core.state import AgentState
from typing import Annotated
import json


def planner_node(state: Annotated[dict, AgentState]) -> dict:
    """规划者智能体：分析需求，生成任务计划"""
    logger.info("[节点日志] 规划者启动")

    question = state.get("question", "")
    logs = state.get("logs", [])

    # 构建 Prompt
    prompt = f"""你是一个专业的任务规划专家。请分析以下研究问题，生成结构化的任务计划。

研究问题：{question}

请按以下 JSON 格式输出计划（不要输出任何其他内容）：
{{
  "topic": "主题名称",
  "research_tasks": [
    "任务1：需要调研的具体方向",
    "任务2：需要收集的数据类型",
    "任务3：需要对比的观点"
  ],
  "writing_strategy": "文章写作策略（如：采用对比分析法，先介绍背景再分析影响最后给出建议）",
  "review_requirements": [
    "审核标准1：数据准确性",
    "审核标准2：逻辑连贯性",
    "审核标准3：观点全面性"
  ]
}}

注意：
- topic：用一句话概括研究主题
- research_tasks 至少包含3个具体调研方向
- writing_strategy 要具体可执行
- review_requirements 要明确可衡量
- 必须输出合法的 JSON 格式"""

    try:
        llm = ChatOpenAI(
            model=OPENAI_MODEL,
            base_url=OPENAI_BASE_URL,
            temperature=0.2,
            api_key=OPENAI_API_KEY
        )
        response = llm.invoke(prompt)
        content = response.content.strip()

        # 尝试解析 JSON
        plan = {}
        try:
            # 清理可能的 Markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            plan = json.loads(content)
        except json.JSONDecodeError:
            logger.warning("JSON 解析失败，使用默认计划")
            plan = {
                'topic': question,
                'research_tasks': ['方向1', '方向2', '方向3'],
                'writing_strategy': '标准结构',
                'review_requirements': ['准确性', '完整性']
            }

        logs.append(f"[规划者] 计划生成完成，主题: {plan.get('topic', '未知')}")
        logger.info(f"[节点日志] 规划者完成 - 输入: {question[:30]}, 输出: topic={plan.get('topic', 'N/A')}")

        return {
            "plan": plan,
            "current_stage": "planning",
            "logs": logs,
            "current_agent": "planner",
            "agent_results": state.get("agent_results", []) + [{"agent": "planner", "status": "completed"}]
        }

    except Exception as e:
        logger.error(f"规划者异常: {e}")
        logs.append(f"[规划者] 异常: {str(e)}")
        # 返回默认计划
        default_plan = {
            "topic": question,
            "research_tasks": ["方向1", "方向2", "方向3"],
            "writing_strategy": "标准结构",
            "review_requirements": ["准确性", "完整性"]
        }
        return {
            "plan": default_plan,
            "current_stage": "planning",
            "logs": logs,
            "current_agent": "planner",
            "agent_results": state.get("agent_results", []) + [{"agent": "planner", "status": "error"}]
        }