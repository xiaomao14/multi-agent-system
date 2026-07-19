'''
写手智能体：根据分析报告撰写文章
'''

from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY, logger
from core.state import AgentState
from typing import Annotated


def writer_node(state: Annotated[dict, AgentState]) -> dict:
    '''写手智能体：根据分析报告撰写文章'''
    logger.info('[节点日志] 写手启动')
    analysis_report = state.get('analysis_report', '')
    question = state.get('question', '')
    plan = state.get('plan', {})

    if not analysis_report:
        logs = state.get('logs', [])
        logs.append('[写手] 没有数据')
        logger.info('[节点日志] 写手完成（无数据）')
        return {
            'draft': '没有分析报告，无法撰写文章。',
            'logs': logs,
            'current_agent': 'writer'
        }

    writing_strategy = plan.get('writing_strategy', '清晰易懂，结构分明')

    prompt = f'''你是一名专业写手。请根据以下分析报告，撰写一篇完整的文章，主题为：{question}

分析报告：
{analysis_report}

写作策略：{writing_strategy}

文章要求：
1. 吸引人的标题
2. 包含背景介绍的开头
3. 3-5个章节，每个章节要有小标题
4. 总结性的结尾
5. 全文约 1500-2500 字

语言要求：使用清晰、通俗易懂的语言，适当举例说明。

请直接输出文章内容，不要包含任何额外说明。'''

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        base_url=OPENAI_BASE_URL,
        temperature=0.7,
        api_key=OPENAI_API_KEY
    )
    response = llm.invoke(prompt)

    logs = state.get('logs', [])
    logs.append(f'[写手] 初稿完成，共 {len(response.content)} 字符')

    # 输入摘要
    input_summary = f'报告长度: {len(analysis_report)} 字符'
    # 输出摘要
    output_summary = f'初稿长度: {len(response.content)} 字符'

    logger.info(f'[节点日志] 写手完成 - 输入: {input_summary}, 输出: {output_summary}')

    return {
        'draft': response.content,
        'logs': logs,
        'current_agent': 'writer',
        'agent_results': state.get('agent_results', []) + [{'agent': 'writer', 'status': 'completed'}]
    }
