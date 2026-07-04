"""
过滤器节点适配层
将 ContentFilter 类转换为 LangGraph 节点函数
"""

from core.config import logger
from core.filters import FilterPipeline


def filter_research_node(state: dict) -> dict:
    """
    过滤器节点：对研究员产出的原始资料进行过滤

    执行时机：研究员 → 过滤器 → 分析师

    过滤内容：
    1. 去重
    2. 相关性评分
    3. 事实核查
    4. 逻辑检查
    """
    logger.info("[节点] 过滤器启动")

    research_data = state.get("research_data", [])
    question = state.get("question", "")

    if not research_data:
        logs = state.get("logs", [])
        logs.append("[过滤器] 没有研究数据，跳过过滤")
        logger.info("[节点] 过滤器完成（无数据）")
        return {
            "research_data": [],
            "logs": logs,
            "current_agent": "filter"
        }

    try:
        # 执行过滤流水线
        pipeline = FilterPipeline(question=question)
        filtered_data = pipeline.execute(research_data)
        filter_logs = pipeline.get_logs()

        # 合并日志到状态
        logs = state.get("logs", [])
        logs.extend(filter_logs)
        logs.append(f"[过滤器] 过滤完成，剩余 {len(filtered_data)} 条资料")

        logger.info("[节点] 过滤器完成")

        return {
            "research_data": filtered_data,
            "logs": logs,
            "current_agent": "filter"
        }

    except Exception as e:
        logger.error(f"[节点] 过滤器执行出错: {e}")
        logs = state.get("logs", [])
        logs.append(f"[过滤器] 过滤出错，保留原始数据: {str(e)}")
        return {
            "research_data": research_data,  # 出错时回退到原始数据
            "logs": logs,
            "current_agent": "filter"
        }