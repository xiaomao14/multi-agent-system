# 多智能体协作文章生成系统 — 使用手册

> **版本**: v2.0  
> **作者**: xiaomao14  
> **更新日期**: 2026-07-18  

---

## 目录

1. [项目简介](#1-项目简介)
2. [系统架构](#2-系统架构)
3. [环境要求](#3-环境要求)
4. [快速开始](#4-快速开始)
5. [详细配置](#5-详细配置)
6. [运行方式](#6-运行方式)
7. [功能说明](#7-功能说明)
8. [常见问题](#8-常见问题)
9. [项目结构](#9-项目结构)
10. [技术支持](#10-技术支持)

---

## 1. 项目简介

本系统是一个基于 **LangGraph** 的多智能体协作平台，能够自动完成从需求分析、资料调研、内容过滤、报告分析、文章写作、质量审稿到修订定稿的完整文章创作流程。

### 核心特性

- **6 个 AI Agent 各司其职**：规划员、研究员、分析师、写手、审稿人、修订写手
- **动态任务规划**：Planner Agent 根据用户需求自动生成结构化任务计划
- **多级内容过滤**：去重 → 相关性评分 → 事实核查 → 逻辑检查
- **修订闭环**：根据审稿意见自动修改文章，输出最终版本
- **双模式运行**：支持命令行交互和 Web 界面两种方式
- **API 兼容**：可使用任意 OpenAI 兼容接口（智谱、通义千问、月之暗面等）

---

## 2. 系统架构

### 工作流程

`
用户输入问题
    |
    v
[Planner 规划员] --> 生成结构化任务计划(JSON)
    |
    +--> [Researcher 研究员] --> 收集调研资料
    |         |
    |         v
    |    [多级过滤] --> 去重/相关性/事实核查/逻辑检查
    |         |
    |         v
    |    [Analyst 分析师] --> 生成分析报告
    |
    +--> [Writer 写手] --> 撰写文章初稿
              |
              v
        [Reviewer 审稿人] --> 输出审稿意见
              |
              v
        [Reviser 修订写手] --> 修改文章输出终稿
`

### 智能体职责表

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| Planner | 任务规划 | 用户问题 | 结构化任务计划(JSON) |
| Researcher | 资料调研 | 任务计划中的调研方向 | 收集的调研资料 |
| Analyst | 数据分析 | 调研资料 | 分析报告 |
| Writer | 文章撰写 | 分析报告 + 写作策略 | 文章初稿 |
| Reviewer | 质量审查 | 初稿 + 审核标准 | 审稿反馈意见 |
| Reviser | 文章修订 | 初稿 + 审稿意见 | 修订后终稿 |

---

## 3. 环境要求

### 必需条件

- **Python**: 3.10 或以上版本
- **操作系统**: Windows / macOS / Linux
- **网络连接**: 需要访问 AI API 服务

### 验证安装

`powershell
# 检查 Python 版本
python --version
# 应显示: Python 3.10.x 或更高

# 检查 pip
pip --version
`

---

## 4. 快速开始

### 第一步：安装依赖

`powershell
pip install -r requirements.txt
`

### 第二步：配置 API 密钥

`powershell
# 复制配置模板
Copy-Item .env.example .env

# 用编辑器打开 .env 文件，填入你的 API 信息
notepad .env
`

### 第三步：运行

`powershell
# 命令行模式
python main.py

# 或 Web 界面
streamlit run app.py
`

---

## 5. 详细配置

### 5.1 API 配置 (.env 文件)

`env
# === 必填配置 ===
# 你的 API 密钥
OPENAI_API_KEY=你的_api_key

# API 端点地址（根据使用的模型服务商填写）
# 智谱 GLM:  https://open.bigmodel.cn/api/paas/v4
# 通义千问:  https://dashscope.aliyuncs.com/compatible-mode/v1
# OpenAI:   https://api.openai.com/v1
# 月之暗面: https://api.moonshot.cn/v1
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# 模型名称（根据服务商提供的模型填写）
# 智谱: glm-4-flash / glm-5
# 通义: qwen-turbo / qwen-plus
# OpenAI: gpt-4o-mini / gpt-4o
OPENAI_MODEL=glm-5.2

# === 可选配置 ===
# 调试模式（true/false）
DEBUG=false

# 日志级别（DEBUG/INFO/WARNING/ERROR）
LOG_LEVEL=INFO
`

### 5.2 支持的 API 服务商

| 服务商 | Base URL | 推荐模型 | 免费额度 |
|--------|----------|----------|----------|
| 智谱 GLM | open.bigmodel.cn | glm-4-flash | 有 |
| 通义千问 | dashscope.aliyuncs.com | qwen-turbo | 有 |
| OpenAI | api.openai.com | gpt-4o-mini | 付费 |
| 月之暗面 | api.moonshot.cn | moonshot-v1-8k | 有 |

> 提示：本项目使用 OpenAI 兼容接口，更换服务商只需修改 OPENAI_BASE_URL 和 OPENAI_MODEL 即可。

### 5.3 日志配置

日志文件保存在 logs/ 目录下，按日期命名（如 20260718.log）。

---

## 6. 运行方式

### 方式一：命令行模式

`powershell
python main.py
`

**交互流程：**

`
============================================================
多智能体协作系统
============================================================
输入你的研究问题，系统将自动完成：调研 -> 过滤 -> 分析 -> 写作 -> 审稿 -> 修订
输入 help 查看帮助
输入 保存 保存当前结果
输入 退出 或 exit 结束程序
============================================================

请输入你的研究问题: AI对就业市场的影响有哪些？

============================================================
研究问题: AI对就业市场的影响有哪些？
============================================================
系统正在处理，请稍候...
   研究员收集资料...
   处理完成...

============================================================
最终文章
============================================================
（文章内容显示在这里）

============================================================
审稿反馈
============================================================
共 5 条建议
  1. [准确性] 某数据已过时，建议更新...
  2. [逻辑性] 第二段与第三段衔接不够自然...
  ...

是否保存结果？(y/n): y
结果已保存到: result_AI对就业市场的影响.txt
`

**可用命令：**

| 命令 | 说明 |
|------|------|
| 输入问题文本 | 开始一次新的协作任务 |
| help / 帮助 | 显示帮助信息 |
| 保存 / save | 保存上一次结果 |
| 退出 / exit / quit | 退出程序 |

### 方式二：Web 界面

`powershell
streamlit run app.py
`

浏览器会自动打开 http://localhost:8501。

**界面功能：**

1. **输入区**: 输入你的研究问题
2. **开始按钮**: 点击后智能体开始协作
3. **任务计划**: 显示 Planner 生成的计划
4. **执行日志**: 可展开查看详细执行过程
5. **审稿反馈**: 显示审稿人的修改建议
6. **生成文章**: 显示最终文章

---

## 7. 功能说明

### 7.1 多智能体协作流程详解

#### Phase 1: 规划 (Planning)

Planner Agent 接收用户问题，使用 LLM 分析任务目标，输出结构化 JSON 计划：

`json
{
  "topic": "AI对就业市场的影响",
  "research_tasks": [
    "AI技术发展历程与现状",
    "受AI影响较大的行业分析",
    "新职业机会与技能需求变化",
    "各国政策应对案例"
  ],
  "writing_strategy": "采用对比分析法，先介绍背景再分析影响最后给出建议",
  "review_requirements": [
    "数据准确性：引用的数据需注明来源和时间",
    "逻辑连贯性：各段落之间过渡自然",
    "观点全面性：涵盖正反两面观点"
  ]
}
`

#### Phase 2: 调研 (Research)

Researcher Agent 根据 Planner 生成的 
esearch_tasks 进行定向资料收集，输出包含关键概念、数据事实、案例和不同观点的结构化资料。

#### Phase 3: 分析 (Analysis)

Analyst Agent 对调研资料进行深度分析，提取核心发现，生成分析报告。

#### Phase 4: 写作 (Writing)

Writer Agent 结合分析报告和 writing_strategy 撰写文章初稿，确保结构完整、论据充分。

#### Phase 5: 审稿 (Review)

Reviewer Agent 根据 
eview_requirements 对初稿进行多维度质量审查，输出具体可操作的修改建议。

#### Phase 6: 修订 (Revision)

Reviser Agent 根据审稿意见对文章进行修改，融合反馈建议，输出最终版本。

### 7.2 多级内容过滤

系统在调研阶段之后、分析阶段之前插入多级过滤模块：

| 过滤层级 | 功能 | 方法 |
|---------|------|------|
| 过滤1：去重 | 去除重复内容，标准化格式 | MD5 哈希比对 |
| 过滤2：相关性 | AI 对每条内容打分，保留高相关项 | LLM 评分（阈值可调） |
| 过滤3：事实核查 | 验证关键数据的准确性 | LLM 交叉验证 |
| 过滤4：逻辑检查 | 检查信息之间的逻辑关系 | LLM 推理分析 |

### 7.3 结果保存

命令行模式下，每次完成任务后可选择保存结果，文件命名规则：

`
result_<问题前30字>.txt
`

保存内容包括：
- 原始研究问题
- 最终文章（修订版优先，无修订版则用初稿）
- 审稿反馈意见

---

## 8. 常见问题

### Q1: 运行时报 ModuleNotFoundError

**原因**: 依赖未正确安装

**解决**:
`powershell
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
`

### Q2: API 调用失败 / 超时

**可能原因**:
1. API Key 无效或过期
2. Base URL 配置错误
3. 网络问题

**排查步骤**:
`powershell
# 1. 检查 .env 文件是否正确加载
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
# 应输出你的 API Key

# 2. 查看日志文件
Get-Content logs\20260718.log
`

### Q3: Streamlit 界面打不开

**解决**:
`powershell
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

### Q5: 如何更换 AI 模型服务商？

只需修改 .env 中的两个配置：

`env
# 示例：切换到通义千问
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-turbo
`

### Q6: 部署到 Streamlit Cloud 后一直报错

**常见原因**:
1. .env 文件中的 API Key 未提交到代码（正确做法：在 Streamlit Cloud 的 Settings -> Secrets 中配置）
2. 依赖安装失败（检查 requirements.txt 是否完整）
3. 启动命令错误（应为 streamlit run app.py）

**解决**:
- 在 Streamlit Cloud 项目设置中添加 OPENAI_API_KEY、OPENAI_MODEL、OPENAI_BASE_URL 三个 Secret
- 确保 .gitignore 中包含 .env

---

## 9. 项目结构

`
multi-agent-system/
|
|-- agents/                    # 智能体模块
|   |-- planner_agent.py       #   规划员：分析需求，生成任务计划
|   |-- researcher.py          #   研究员：定向资料收集
|   |-- analyst.py             #   分析师：数据分析与报告生成
|   |-- writer.py              #   写手：文章撰写
|   |-- reviewer.py            #   审稿人：质量审查
|   |-- reviser.py             #   修订写手：根据反馈修改文章
|
|-- core/                      # 核心模块
|   |-- graph.py               #   LangGraph 工作流图构建
|   |-- state.py               #   状态定义（TypedDict）
|   |-- config.py              #   配置加载（.env）
|   |-- filters.py             #   内容过滤逻辑
|   |-- filter_nodes.py        #   过滤节点集成
|
|-- utils/                     # 工具模块
|   |-- logger.py              #   日志配置
|
|-- templates/                 # 模板文件
|
|-- logs/                      # 运行日志（按日期）
|
|-- app.py                     # Streamlit Web 界面
|-- main.py                    # 命令行交互入口
|-- requirements.txt           # Python 依赖列表
|-- .env.example               # 环境变量配置模板
|-- .env                       # 实际配置（不提交到 Git）
|-- .gitignore                 # Git 忽略规则
|-- USAGE.md                   # 本使用手册
|-- README.md                  # 项目简介（GitHub 展示用）
`

---

## 10. 技术支持

| 联系方式 | 说明 |
|----------|------|
| GitHub | xiaomao14/multi-agent-system |
| 问题反馈 | 提交 Issue |
| 文档 | 本文件 + README.md |

---

*本手册随项目版本同步更新，如有不一致请以最新代码为准。*
