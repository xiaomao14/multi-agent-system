"""
HumanReview 节点：等待人工审批结果
这是一个被动节点，不执行任何 AI 逻辑，仅由 Streamlit UI 触发。
"""

from core.config import logger


def human_review_node(state: dict) -> dict:
    """
    人工审核节点
    
    这个节点本身不做任何事，真正的逻辑在 Streamlit UI 中：
    - 用户通过 / 拒绝 / 修改意见 输入框做出决策
    - 决策结果存入 st.session_state.human_decision
    - 节点读取该决策并返回对应的状态更新
    
    Args:
        state: 当前工作流状态
        
    Returns:
        包含 human_review_status 的状态字典
    """
    logger.info("[节点日志] 人工审核节点等待决策...")
    
    # 检查是否有来自 UI 的决策
    decision = state.get("_human_decision", "approved")
    comment = state.get("_human_comment", "")
    
    if decision == "approved":
        logs = state.get("logs", [])
        logs.append("[人工审核] 审批通过，进入终稿编辑")
        logger.info("[节点日志] 人工审核通过")
        return {
            "human_review_status": "approved",
            "human_review_comment": "",
            "logs": logs,
            "current_agent": "human_review",
            "current_stage": "human_approved"
        }
    
    elif decision == "rejected":
        logs = state.get("logs", [])
        logs.append(f"[人工审核] 审批拒绝，意见: {comment}")
        logger.info(f"[节点日志] 人工审核拒绝 - 意见: {comment}")
        return {
            "human_review_status": "rejected",
            "human_review_comment": comment,
            "logs": logs,
            "current_agent": "human_review",
            "current_stage": "human_rejected"
        }
    
    else:
        logs = state.get("logs", [])
        logs.append(f"[人工审核] 未知决策: {decision}")
        return {
            "human_review_status": "pending",
            "human_review_comment": "",
            "logs": logs,
            "current_agent": "human_review",
            "current_stage": "human_pending"
        }