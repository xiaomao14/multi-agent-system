'''
分析师智能体：分析研究资料
'''

from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY, logger
from core.state import AgentState
from typing import Annotated


def analyst_node(state: Annotated[dict, AgentState]) -> dict:
    '''分析师智能体：分析研究资料'''
    logger.info('[节点日志] 分析师启动')
    research_data = state.get('research_data', [])
    question = state.get('question', '')
    plan = state.get('plan', {})

    if not research_data:
        logs = state.get('logs', [])
        logs.append('[分析师] 没有数据')
        logger.info('[节点日志] 分析师完成（无数据）')
        return {
            'analysis_report': '没有可分析的数据。',
            'logs': logs,
            'current_agent': 'analyst'
        }

    prompt = f'''你是一名数据分析师。请针对以下研究资料进行分析，研究问题为：{question}

研究资料：
{'\\n'.join(research_data)}

请按以下格式输出分析报告：
1. 核心摘要（1-3句话）
2. 主要发现（3-5点）
3. 数据洞察
4. 可执行的结论

请确保分析深入、逻辑清晰、语言简洁。'''

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        base_url=OPENAI_BASE_URL,
        temperature=0.5,
        api_key=OPENAI_API_KEY
    )
    response = llm.invoke(prompt)

    logs = state.get('logs', [])
    logs.append('[分析师] 报告生成完成')

    # 输入摘要
    input_summary = f'资料条数: {len(research_data)}, 问题: {question[:50]}...'
    # 输出摘要
    output_summary = f'报告长度: {len(response.content)} 字符'

    logger.info(f'[节点日志] 分析师完成 - 输入: {input_summary}, 输出: {output_summary}')

    return {
        'analysis_report': response.content,
        'logs': logs,
        'current_agent': 'analyst',
        'agent_results': state.get('agent_results', []) + [{'agent': 'analyst', 'status': 'completed'}]
    }
