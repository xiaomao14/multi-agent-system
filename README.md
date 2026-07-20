# Multi-Agent Article Generation System

基于 LangGraph 的多智能体协作文章生成系统，能够自动完成从需求分析、资料调研、内容过滤、分析报告、文章写作、质量审校到修订定稿的完整文章创作流程。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.50+-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

---

## ✨ 核心特性

- **6 个 AI Agent 各司其职**：规划员、研究员、分析师、写手、审稿人、修订写手
- **动态任务规划**：Planner Agent 根据用户需求自动生成结构化任务计划
- **多级内容过滤**：去重 → 相关性评分 → 事实核查 → 逻辑检查
- **修订闭环**：根据审稿意见自动修改文章，输出最终版本
- **双模式运行**：支持命令行交互和 Web 界面两种方式
- **API 兼容**：可使用任意 OpenAI 兼容接口（智谱、通义千问、月之暗面等）

---

## 🛠 技术栈

| 组件 | 技术 | 作用 |
|------|------|------|
| 框架 | LangGraph | 多智能体工作流编排 |
| LLM | 智谱 GLM-4/5 | 智能体核心推理 |
| Web | Streamlit | 交互式可视化界面 |
| 存储 | SQLite | 对话记忆持久化 |
| 日志 | Python logging | 运行日志追踪 |

---

## 📁 项目结构

`
multi-agent-system/
├── agents/                    # 智能体模块
│   ├── planner_agent.py       #   规划员：分析需求，生成任务计划
│   ├── researcher.py          #   研究员：定向资料收集
│   ├── analyst.py             #   分析师：数据分析与报告生成
│   ├── writer.py              #   写手：文章撰写
│   ├── reviewer.py            #   审稿人：质量审查
│   ├── reviser.py             #   修订写手：根据反馈修改文章
│   ├── human_review.py        #   人工审核节点
│   └── final_editor.py        #   终稿编辑
├── core/                      # 核心模块
│   ├── graph.py               #   LangGraph 工作流图构建
│   ├── state.py               #   状态定义（TypedDict）
│   ├── config.py              #   配置加载（.env）
│   ├── filters.py             #   内容过滤逻辑
│   ├── filter_nodes.py        #   过滤节点集成
│   └── memory.py              #   对话记忆管理
├── utils/                     # 工具模块
│   ├── logger.py              #   日志配置
├── logs/                      # 运行日志（按日期）
├── data/                      # 数据存储
│   └── memory.db              #   SQLite 对话记忆库
├── app.py                     # Streamlit Web 界面
├── main.py                    # 命令行交互入口
├── requirements.txt           # Python 依赖列表
├── .env.example               # 环境变量配置模板
├── .env                       # 实际配置（不提交到 Git）
├── .gitignore                 # Git 忽略规则
├── USAGE.md                   # 使用手册
└── README.md                  # 项目介绍（GitHub 展示用）
`

---

## 🚀 快速开始

### 1. 安装依赖

`ash
pip install -r requirements.txt
`

### 2. 配置 API Key

复制 .env.example 为 .env，填入你的智谱 AI API Key：

`ash
cp .env.example .env
`

编辑 .env 文件：

`env
# 必填配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4-flash

# 可选配置
DEBUG=false
LOG_LEVEL=INFO
`

> **获取 API Key**：前往 [智谱开放平台](https://open.bigmodel.cn/) 注册并创建 API Key，新用户有免费额度。

### 3. 运行

`ash
# 命令行模式
python main.py

# 或 Web 界面模式
streamlit run app.py
`

浏览器访问 http://localhost:8501 开始使用。

---

## 🤖 智能体协作流程

`
用户输入问题
    ↓
[Planner 规划员] → 生成结构化任务计划 (JSON)
    ↓
├── [Researcher 研究员] → 收集调研资料
│       ↓
│   [多级过滤] → 去重/相关性/事实核查/逻辑检查
│       ↓
│   [Analyst 分析师] → 生成分析报告
│
└── [Writer 写手] → 撰写文章初稿
        ↓
    [Reviewer 审稿人] → 输出审稿意见
        ↓
    [Reviser 修订写手] → 修改文章输出终稿
`

### 智能体职责表

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| Planner | 任务规划 | 用户问题 | 结构化任务计划 (JSON) |
| Researcher | 资料调研 | 任务计划中的调研方向 | 收集的调研资料 |
| Analyst | 数据分析 | 调研资料 | 分析报告 |
| Writer | 文章撰写 | 分析报告 + 写作策略 | 文章初稿 |
| Reviewer | 质量审查 | 初稿 + 审核标准 | 审稿反馈意见 |
| Reviser | 文章修订 | 初稿 + 审稿意见 | 修订后终稿 |

---

## ⚙️ 配置说明

### API 配置

支持多种 OpenAI 兼容接口：

`env
# 智谱 GLM
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4-flash

# 通义千问
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-turbo

# OpenAI
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# 月之暗面
OPENAI_BASE_URL=https://api.moonshot.cn/v1
OPENAI_MODEL=moonshot-v1-8k
`

### 调试模式

`env
DEBUG=true          # 开启详细日志
LOG_LEVEL=DEBUG     # 日志级别：DEBUG/INFO/WARNING/ERROR
`

---

## 📊 内容过滤机制

系统内置四级内容过滤管道，确保调研资料质量：

| 过滤层级 | 作用 | 技术手段 |
|----------|------|----------|
| 过滤1：去重 | 消除重复信息 | 文本相似度比对 |
| 过滤2：相关性评分 | 筛选高质量资料 | LLM 评分（阈值可调） |
| 过滤3：事实核查 | 验证关键数据的准确性 | LLM 交叉验证 |
| 过滤4：逻辑检查 | 检查信息之间的逻辑关系 | LLM 推理分析 |

---

## 🎯 应用场景

- **学术研究**：自动生成文献综述、研究计划
- **行业分析**：快速产出市场分析报告
- **技术文档**：自动化编写技术白皮书
- **新闻写作**：基于多源资料的深度报道
- **教育辅助**：生成学习资料和课程大纲

---

## ❓ 常见问题

### Q1: 运行时报 ModuleNotFoundError

**原因**: 依赖未正确安装

**解决**:
`ash
pip install -r requirements.txt --force-reinstall
`

### Q2: API 调用失败 / 超时

**可能原因**:
1. API Key 无效或过期
2. Base URL 配置错误
3. 网络问题

**排查步骤**:
`ash
# 1. 检查 .env 文件是否正确加载
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"

# 2. 查看日志文件
Get-Content logs\20260719.log
`

### Q3: Streamlit 界面打不开

**解决**:
`ash
# 确认 Streamlit 已安装
pip install streamlit

# 手动指定端口
streamlit run app.py --server.port 8502
`

### Q4: 生成的文章质量不高

**优化建议**:
1. 更换更强的模型（如从 glm-4-flash 升级到 glm-5）
2. 调整 Prompt，提供更具体的指令
3. 降低 temperature 参数使输出更稳定
4. 在 .env 中设置 LOG_LEVEL=DEBUG 查看详细日志

---

## 🔮 扩展方向

- [ ] 支持更多文档格式（PDF、Word、PPT）
- [ ] 添加团队协作功能
- [ ] 集成外部知识库（RAG）
- [ ] 支持多语言输出
- [ ] 添加模型对比评测功能
- [ ] Docker 容器化部署

---

## 📄 License

MIT License

---

## 👤 作者

**xiaomao14**

- GitHub: [xiaomao14](https://github.com/xiaomao14)
- 项目: [multi-agent-system](https://github.com/xiaomao14/multi-agent-system)

---

*本项目仅供学习和研究使用。*