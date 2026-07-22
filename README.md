# Multi-Agent Collaboration System - 改造记录

## 项目概述

基于 LangGraph 的多智能体协作系统，能够自动完成"需求分析 → 资料调研 → 内容过滤 → 报告分析 → 文章写作 → 质量审稿 → 修订定稿"的完整文章创作流程。

**作者**: xiaomao14  
**更新日期**: 2026-07-22  
**版本**: v2.5  

---

## 核心特性

### 已实现功能

1. **6 个 AI Agent 协同工作**
   - Planner（规划员）：分析需求，生成结构化任务计划
   - Researcher（研究员）：定向资料收集
   - Analyst（分析师）：数据分析与报告生成
   - Writer（写手）：文章撰写
   - Reviewer（审稿人）：质量审查
   - FinalEditor（终审编辑）：根据审核意见修订文章

2. **动态任务规划**
   - Planner Agent 根据用户需求自动生成结构化 JSON 计划
   - 包含调研方向、写作策略、审核标准

3. **多级内容过滤**
   - 过滤 1：去重（MD5 哈希比对）
   - 过滤 2：相关性评分（AI 打分，阈值可调）
   - 过滤 3：事实核查（LLM 交叉验证）
   - 过滤 4：逻辑检查（LLM 推理分析）

4. **修订闭环**
   - 根据审稿意见自动修改文章，输出最终版本

5. **双模式运行**
   - 命令行交互模式（python main.py）
   - Web 界面模式（streamlit run app.py）

6. **API 兼容**
   - 支持 OpenAI 兼容接口
   - 可使用智谱 GLM、通义千问、月之暗面等

7. **人类在环审核（Human-in-the-Loop）**
   - 审稿完成后暂停，等待人工决策
   - 支持批准通过 / 拒绝并重写 / 提出修改意见
   - 人类意见优先级高于 AI 审稿意见

8. **实时进度反馈**
   - 进度条显示当前阶段
   - 每个 Agent 完成时更新进度

9. **会话记忆系统**
   - SQLite 持久化存储每次任务结果
   - 支持查看历史任务列表
   - 支持基于历史结果继续修改文章

---

## 系统架构

### 完整工作流程

`
用户输入问题
    │
    ▼
┌─────────────┐
│  Planner    │ ← 分析需求，生成结构化任务计划
│  (规划员)   │    包含：调研方向、写作策略、审核标准
└──────┬──────┘
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
┌─────────────┐                      ┌─────────────┐
│ Researcher  │                      │  Writer     │
│  (研究员)   │                      │  (写手)     │
│  • 收集资料  │                      │  • 撰写初稿  │
│  • 基于计划  │                      │  • 遵循策略  │
└──────┬──────┘                      └──────┬──────┘
       │                                     │
       ▼                                     ▼
┌─────────────┐                      ┌─────────────┐
│ Filter      │                      │  Reviewer   │
│  (过滤器)   │                      │  (审稿人)   │
│  • 去重     │                      │  • 质量审查  │
│  • 相关性   │                      │  • 提建议   │
└──────┬──────┘                      └──────┬──────┘
       │                                     │
       ▼                                     ▼
┌─────────────┐                      ┌─────────────┐
│  Analyst    │                      │  Human      │
│  (分析师)   │                      │  Review     │
│  • 分析数据  │                      │  (人工审核)  │
│  • 生成报告  │                      │  • 批准/拒绝 │
└──────┬──────┘                      └──────┬──────┘
       │                                     │
       └──────────────┬──────────────────────┘
                      ▼
               ┌─────────────┐
               │ FinalEditor │
               │  (终审编辑)  │
               │  • 采纳反馈  │
               │  • 修改文章  │
               └──────┬──────┘
                      ▼
               ┌─────────────┐
               │ Final Article│
               │   (终稿)    │
               └─────────────┘
`

### 智能体职责表

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| Planner | 任务规划 | 用户问题 | 结构化任务计划(JSON) |
| Researcher | 资料调研 | 任务计划中的调研方向 | 收集的调研资料 |
| Analyst | 数据分析 | 调研资料 | 分析报告 |
| Writer | 文章撰写 | 分析报告 + 写作策略 | 文章初稿 |
| Reviewer | 质量审查 | 初稿 + 审核标准 | 审稿反馈意见 |
| HumanReview | 人工审核 | 审稿结果 | 批准/拒绝/修改意见 |
| FinalEditor | 终审编辑 | 初稿 + 审核意见 | 最终文章 |

---

## 环境要求

### 必需条件

- **Python**: 3.10 或以上版本
- **操作系统**: Windows / macOS / Linux
- **网络连接**: 需要访问 AI API 服务

### 安装依赖

`powershell
pip install -r requirements.txt
`

### 支持的 API 服务商

| 服务商 | Base URL | 推荐模型 | 免费额度 |
|--------|----------|----------|----------|
| 智谱 GLM | open.bigmodel.cn | glm-4-flash | ✅ 有 |
| 通义千问 | dashscope.aliyuncs.com | qwen-turbo | ✅ 有 |
| OpenAI | api.openai.com | gpt-4o-mini | ❌ 付费 |
| 月之暗面 | api.moonshot.cn | moonshot-v1-8k | ✅ 有 |

---

## 快速开始

### 命令行模式

`powershell
python main.py
`

### Web 界面

`powershell
streamlit run app.py
`

浏览器会自动打开 http://localhost:8501

---

## 配置文件说明

### .env 文件

`env
# === 必填配置 ===
OPENAI_API_KEY=你的_api_key
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-5.2

# === 可选配置 ===
DEBUG=false
LOG_LEVEL=INFO
`

---

## 项目结构

`
multi-agent-system/
│
├── agents/                    # 智能体模块
│   ├── planner_agent.py       #   规划员
│   ├── researcher.py          #   研究员
│   ├── analyst.py             #   分析师
│   ├── writer.py              #   写手
│   ├── reviewer.py            #   审稿人
│   ├── human_review.py        #   人工审核节点
│   ├── final_editor.py        #   终审编辑
│   └── reviser.py             #   修订写手（备用）
│
├── core/                      # 核心模块
│   ├── graph.py               #   LangGraph 工作流图
│   ├── state.py               #   状态定义
│   ├── config.py              #   配置加载
│   ├── memory.py              #   会话记忆管理器
│   ├── filters.py             #   内容过滤逻辑
│   └── filter_nodes.py        #   过滤节点集成
│
├── utils/                     # 工具模块
│   └── logger.py              #   日志配置
│
├── templates/                 # 模板文件
├── logs/                      # 运行日志（按日期）
├── data/                      # 记忆数据库
│   └── memory.db              #   SQLite 数据库
│
├── app.py                     # Streamlit Web 界面
├── main.py                    # 命令行交互入口
├── requirements.txt           # Python 依赖列表
├── .env.example               # 环境变量配置模板
├── .env                       # 实际配置（不提交到 Git）
├── .gitignore                 # Git 忽略规则
├── USAGE.md                   # 使用手册
└── README.md                  # 项目简介
`

---

## 常见问题

### Q1: 运行时报 ModuleNotFoundError

**原因**: 依赖未正确安装

**解决**:
`powershell
pip install -r requirements.txt --force-reinstall
`

### Q2: API 调用失败 / 超时

**排查步骤**:
1. 检查 API Key 是否正确
2. 确认 Base URL 配置正确
3. 检查网络连接
4. 查看日志文件：logs\YYYYMMDD.log

### Q3: Streamlit 界面打不开

**解决**:
`powershell
pip install streamlit
streamlit run app.py --server.port 8502
`

### Q4: 生成的文章质量不高

**优化建议**:
1. 更换更强的模型
2. 调整 Prompt
3. 降低 temperature 参数
4. 设置 LOG_LEVEL=DEBUG 查看详细日志

---

## 更新日志

### v2.5 (2026-07-22)
- [新增] Human-in-the-Loop 人工审核机制
- [新增] Real-time progress bar 实时进度条
- [新增] MemoryManager 会话记忆系统
- [修改] 工作流图增加 human_review 节点
- [修改] app.py 分步渲染 + 人工决策 UI
- [修复] planner_agent.py 和 researcher.py 中 topic 拼写错误

### v2.0 (2026-07-18)
- [新增] Planner Agent 动态任务规划
- [新增] 多级内容过滤模块
- [新增] SQLite 持久化存储
- [新增] Web 界面任务计划展示
- [修改] graph.py 重构为动态流程

### v1.0 (2026-07-01)
- [初始版本] 基础多智能体协作系统
- [支持] 研究员、分析师、写手、审稿人
- [双模式] 命令行 + Web 界面

---

*本记录随项目版本同步更新，如有不一致请以最新代码为准。*
