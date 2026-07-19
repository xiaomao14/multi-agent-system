import streamlit as st
from core.graph import run_workflow
from core.memory import get_memory_manager
from core.config import logger

# ========== 页面配置 ==========
st.set_page_config(
    page_title="多智能体协作系统",
    page_icon="robot",
    layout="wide"
)

# ========== 侧边栏：会话管理 ==========
with st.sidebar:
    st.header("会话管理")

    if st.button("新建会话", type="primary", use_container_width=True):
        sid = get_memory_manager().create_session()
        st.session_state.current_session_id = sid
        st.session_state.history_loaded = False
        st.rerun()

    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = get_memory_manager().create_session()

    session_id = st.session_state.current_session_id
    st.info(f"当前会话: {session_id}")

    if "history_loaded" not in st.session_state:
        st.session_state.history_loaded = False

    if st.button("刷新历史记录", use_container_width=True):
        st.session_state.history_loaded = True
        st.rerun()

    if st.session_state.history_loaded:
        history = get_memory_manager().get_session_history(session_id, limit=20)
        if history:
            st.subheader("历史任务")
            for task in history:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.caption(task.get("question", "")[:40] + "...")
                    with col2:
                        if st.button("使用", key=f"use_{task['id']}"):
                            st.session_state.continue_task = task
                            st.rerun()
        else:
            st.caption("暂无历史任务")

# ========== 主界面 ==========
st.title("多智能体协作文章生成系统")
st.markdown("输入一个问题，AI 智能体将协同完成调研、分析、写作和审稿。")

# ========== 继续修改模式 ==========
continue_task = st.session_state.get("continue_task")
if continue_task:
    with st.expander("继续修改模式：基于上一版本修改", expanded=True):
        st.markdown(f"**上次问题**: {continue_task.get('question', 'N/A')}")
        st.markdown(f"**上次主题**: {continue_task.get('topic', 'N/A')}")
        st.caption(f"任务ID: {continue_task.get('id', 'N/A')}")
        st.info("系统将以上一版本的终稿为基础，重新生成任务计划并继续修改。")
        if st.button("取消继续模式", use_container_width=True):
            del st.session_state.continue_task
            st.rerun()

# ========== 用户输入 ==========
question = st.text_area(
    "请输入你的研究问题：",
    placeholder="例如：AI对就业市场的影响有哪些？",
    height=100
)

# 传递 continue_task
if "continue_task" in st.session_state and question:
    ct = st.session_state.pop("continue_task")
else:
    ct = None

# ========== 运行按钮 ==========
if st.button("开始协作", type="primary", disabled=not question):
    st.session_state._running_question = question
    st.session_state._running_session_id = session_id
    st.session_state._running_continue_task = ct
    st.session_state.step = "step1_running"
    st.rerun()

# ========== 执行工作流（分步渲染 + 实时进度条） ==========
running_question = st.session_state.get("_running_question")
running_session_id = st.session_state.get("_running_session_id")
running_continue_task = st.session_state.get("_running_continue_task")

if running_question:
    if "step" not in st.session_state:
        st.session_state.step = "step1_running"

    # ---- 进度条 ----
    step = st.session_state.step
    progress_map = {
        "step1_running": (0.15, "🔍 规划员分析任务..."),
        "step1_done":     (0.25, "✅ 规划完成，正在调研..."),
        "step2_done":     (0.40, "✅ 调研完成，正在分析..."),
        "step3_done":     (0.55, "✅ 分析完成，正在写作..."),
        "step4_done":     (0.70, "✅ 写作完成，AI 正在审稿..."),
        "step5_waiting":  (0.80, "⏳ 等待人工审核..."),
        "step6_done":     (0.90, "✅ 审核完成，正在生成终稿..."),
        "step7_done":     (1.0,  "✅ 全部完成！"),
    }
    current_prog, current_msg = progress_map.get(step, (0, ""))
    st.progress(current_prog, text=current_msg)

    try:
        # ===================== Step 1: 运行到审稿人 =====================
        if step == "step1_running":
            from langgraph.graph import StateGraph, END
            from core.state import AgentState
            from agents.planner_agent import planner_node
            from agents.researcher import researcher_node
            from agents.analyst import analyst_node
            from agents.writer import writer_node
            from agents.reviewer import reviewer_node
            from core.filter_nodes import filter_research_node

            pw = StateGraph(AgentState)
            pw.add_node("planner", planner_node)
            pw.add_node("researcher", researcher_node)
            pw.add_node("filter", filter_research_node)
            pw.add_node("analyst", analyst_node)
            pw.add_node("writer", writer_node)
            pw.add_node("reviewer", reviewer_node)
            pw.set_entry_point("planner")
            pw.add_edge("planner", "researcher")
            pw.add_edge("researcher", "filter")
            pw.add_edge("filter", "analyst")
            pw.add_edge("analyst", "writer")
            pw.add_edge("writer", "reviewer")

            pw_app = pw.compile()

            initial_state = {
                "question": running_question,
                "plan": {}, "current_stage": "",
                "agent_results": [], "research_data": [],
                "analysis_report": "", "draft": "",
                "review_feedback": [],
                "human_review_status": "pending",
                "human_review_comment": "",
                "final_article": "",
                "logs": [], "current_agent": ""
            }

            if running_continue_task:
                topic = running_continue_task.get("topic", "N/A")
                initial_state["draft"] = running_continue_task.get(
                    "final_article", running_continue_task.get("draft", "")
                )
                initial_state["review_feedback"] = running_continue_task.get("review_feedback", [])
                initial_state["logs"].append(f"[系统] 基于历史任务继续修改，上一任务: {topic}")
                prev_len = len(initial_state.get("draft", "0"))
                initial_state["logs"].append(f"[系统] 上一篇文章长度: {prev_len} 字符")

            st.session_state.partial_result = pw_app.invoke(initial_state)
            st.session_state.initial_state = initial_state
            st.session_state.step = "step5_waiting"
            st.rerun()

        # ===================== Step 2: 展示审稿结果 + 人工审核 =====================
        elif step == "step5_waiting":
            result = st.session_state.partial_result
            initial_state = st.session_state.initial_state

            st.markdown("---")

            # 任务计划
            plan = result.get("plan", {})
            if plan:
                st.subheader("📋 任务计划")
                st.markdown(f"**主题**: {plan.get('topic', '未指定')}")
                if plan.get("research_tasks"):
                    st.markdown("**调研方向**")
                    for i, task in enumerate(plan["research_tasks"], 1):
                        st.markdown(f"{i}. {task}")
                if plan.get("writing_strategy"):
                    st.markdown(f"**写作策略**: {plan['writing_strategy']}")
                if plan.get("review_requirements"):
                    st.markdown("**审核标准**")
                    for req in plan["review_requirements"]:
                        st.markdown(f"- {req}")
                st.markdown("---")

            # 初稿
            st.subheader("✍️ 文章初稿")
            draft = result.get("draft", "")
            st.markdown(draft)

            # AI 审稿意见
            st.subheader("🔍 AI 审稿意见")
            feedback_list = result.get("review_feedback", [])
            if feedback_list:
                for fb in feedback_list:
                    st.markdown(f"- {fb}")
            else:
                st.caption("无审稿意见")
            st.markdown("---")

            # 人工审核面板
            st.subheader("👤 人工审核")
            st.info("请对以上文章进行审阅，选择以下操作之一：")

            col1, col2, col3 = st.columns(3)
            with col1:
                approve = st.button("✅ 批准通过", type="primary", use_container_width=True)
            with col2:
                reject = st.button("❌ 拒绝并重写", use_container_width=True)
            with col3:
                edit = st.button("✏️ 提出修改意见", use_container_width=True)

            human_comment = st.text_area(
                "修改意见（可选）",
                placeholder="例如：第二段数据过时了，请更新为最新数据...",
                height=80
            )

            if approve:
                st.session_state.human_decision = "approved"
                st.session_state.human_comment = human_comment
                st.session_state.step = "step6_done"
                st.rerun()
            elif reject:
                st.session_state.human_decision = "rejected"
                st.session_state.human_comment = human_comment
                st.session_state.step = "step6_done"
                st.rerun()
            elif edit:
                st.session_state.human_decision = "edited"
                st.session_state.human_comment = human_comment
                st.session_state.step = "step6_done"
                st.rerun()

            if "human_decision" not in st.session_state:
                st.warning("⏳ 请选择一项操作：批准、拒绝或提出修改意见")

        # ===================== Step 3: 终审编辑 =====================
        elif step == "step6_done":
            from langgraph.graph import StateGraph, END
            from core.state import AgentState
            from agents.human_review import human_review_node
            from agents.final_editor import final_editor_node

            initial_state = st.session_state.initial_state
            initial_state["human_review_status"] = st.session_state.human_decision
            initial_state["human_review_comment"] = st.session_state.human_comment

            fg = StateGraph(AgentState)
            fg.add_node("human_review", human_review_node)
            fg.add_node("final_editor", final_editor_node)
            fg.set_entry_point("human_review")
            fg.add_edge("human_review", "final_editor")
            fg.add_edge("final_editor", END)

            fg_app = fg.compile()
            result = fg_app.invoke(initial_state)

            task_id = get_memory_manager().save_task(
                running_session_id, result, running_question
            )
            result["task_id"] = task_id
            result["session_id"] = running_session_id

            st.session_state.step = "step7_done"
            st.session_state.final_result = result
            st.session_state.task_id = task_id
            st.rerun()

        # ===================== Step 4: 展示最终结果 =====================
        elif step == "step7_done":
            result = st.session_state.final_result
            task_id = st.session_state.task_id

            st.markdown("---")
            st.subheader("📝 执行日志")
            logs = result.get("logs", [])
            for log in logs:
                st.text(log)

            st.markdown("---")
            st.subheader("👤 人工审核结果")
            decision = st.session_state.get("human_decision", "approved")
            if decision == "approved":
                st.success("✅ 人工审核通过")
            elif decision == "rejected":
                st.error("❌ 人工审核拒绝")
            else:
                st.info("✏️ 人工审核：提出修改意见")
            if st.session_state.get("human_comment"):
                st.markdown(f"**修改意见**: {st.session_state['human_comment']}")

            st.markdown("---")
            st.subheader("📄 最终文章")
            st.markdown(result.get("final_article", ""))

            st.success("🎉 本次任务完成！")
            st.caption(f"任务ID: {task_id} | 会话ID: {running_session_id}")

            # 清除运行状态
            for key in ["step", "_running_question", "_running_session_id",
                        "_running_continue_task", "partial_result",
                        "initial_state", "human_decision", "human_comment",
                        "final_result", "task_id"]:
                if key in st.session_state:
                    del st.session_state[key]

    except Exception as e:
        st.error(f"❌ 错误: {e}")
        logger.error(f"Streamlit error: {e}")
        for key in ["step", "_running_question", "_running_session_id",
                    "_running_continue_task", "partial_result",
                    "initial_state", "human_decision", "human_comment",
                    "final_result", "task_id"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()