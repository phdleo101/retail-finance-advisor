# 零售金融智能顾问 (Retail Finance AI Advisor)

> [English](README_EN.md) | 中文

> 基于风险测评的智能理财产品推荐与资产配置系统

[![在线Demo](https://img.shields.io/badge/在线Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://retail-finance-advisor-jwhilqzhrdnwwp2zzfpnue.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-代码仓库-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/phdleo101/retail-finance-advisor)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

## 项目简介

本项目是一个零售金融智能顾问系统，通过交互式风险测评问卷评估投资者风险承受能力（C1-C5五级），基于风险等级匹配适合的理财产品（50款产品库），并通过标准普尔四象限模型生成个性化资产配置方案。

**核心定位**：投资参考工具（非投资建议），符合金融监管适当性管理要求。

## 功能特性

- **风险测评**：10题交互式问卷 → C1-C5五级评分 → 各维度可视化
- **产品推荐**：50款理财产品 → 风险等级匹配 → 多维度筛选排序
- **智能问答**：Dify RAG流式问答 → 金融知识库 → 本地降级
- **资产配置**：标准普尔四象限 → 投资金额分配 → Plotly交互可视化

## 技术架构

```
用户（浏览器访问 Streamlit）
        ↓
Streamlit 前端（4个Tab）
├── 风险测评：交互式问卷 + 评分算法 + 各维度柱状图
├── 产品推荐：风险等级匹配 + 筛选排序 + 产品卡片
├── 智能问答：Dify RAG 流式 SSE + LRU缓存 + 本地降级
└── 资产配置：标普四象限 + Plotly饼图 + 投资组合表
        ↓
Python 逻辑层                    Dify RAG 引擎
├── 风险评分算法（C1-C5）         ├── 金融产品知识库
├── 产品匹配引擎（R1-R5）         ├── 金融法规合规库
└── 标普四象限分配模型            └── 投资科普库
        ↓
数据层：products.json(50款) + risk_questions.json(10题) + finance_kb.md
```

## 快速开始

### 1. 本地运行

```bash
pip install -r requirements.txt
streamlit run src/streamlit_app.py
```

### 2. 配置 Dify RAG（可选）

复制 `.streamlit/secrets.toml.example` 为 `.streamlit/secrets.toml`，填入 Dify API 配置。

不配置也可使用，系统自动降级为本地知识库模式。

### 3. 在线Demo

**💰 立即体验**：[零售金融智能顾问在线Demo](https://retail-finance-advisor-jwhilqzhrdnwwp2zzfpnue.streamlit.app/)

打开链接即可使用，无需注册登录。试试：
1. 在「风险测评」Tab 完成 10 道题，获取你的 C1-C5 风险等级
2. 在「产品推荐」Tab 查看适合你风险等级的 50 款理财产品
3. 在「资产配置」Tab 输入投资金额，查看标准普尔四象限配置方案
4. 在「智能问答」Tab 咨询理财产品、风险等级等金融问题

## 数据说明

### 理财产品库（50款）

| 风险等级 | 产品数量 | 典型产品 |
|---|---|---|
| R1 低风险 | 10款 | 活期存款、大额存单、货币基金 |
| R2 中低风险 | 10款 | 储蓄国债、纯债基金、银行理财R2 |
| R3 中风险 | 10款 | 混合基金、可转债基金、REITs |
| R4 中高风险 | 10款 | 股票基金、指数基金、QDII |
| R5 高风险 | 10款 | 行业主题基金、私募基金、结构化理财 |

### 风险测评题库（10题）

覆盖维度：年龄、收入、投资经验、金融知识、投资目标、亏损承受、投资期限、资产占比、收益偏好、投资心态

### 标准普尔四象限

| 象限 | 名称 | 标准比例 | 用途 |
|---|---|---|---|
| 第一 | 要花的钱 | 10% | 3-6个月日常开销 |
| 第二 | 保命的钱 | 20% | 意外重疾保障 |
| 第三 | 生钱的钱 | 30% | 追求高收益 |
| 第四 | 保本升值的钱 | 40% | 养老/教育金 |


## 项目结构

```
retail-finance-advisor/
├── src/
│   ├── streamlit_app.py          # 主应用（4个Tab）
│   ├── risk_engine.py            # 风险评分引擎
│   ├── product_engine.py         # 产品推荐引擎
│   └── rag_engine.py             # RAG问答引擎
├── data/
│   ├── products.json             # 50款理财产品数据
│   ├── risk_questions.json       # 10道风险测评题
│   └── knowledge/
│       └── finance_kb.md         # 金融知识库
├── docs/
│   └── 01-design-document.md     # 方案设计文档
├── .streamlit/
│   ├── config.toml               # Streamlit配置
│   └── secrets.toml.example      # Secrets模板
├── requirements.txt
└── README.md
```

## 合规声明

- 本系统仅提供投资参考，不构成投资建议或理财产品销售
- 投资者适当性管理：C1-C5只能购买对应风险等级及以下产品
- 遵守资管新规：禁止刚性兑付，净值化运作
- 投资有风险，入市需谨慎

## 技术栈

- **前端**：Streamlit
- **RAG**：Dify Cloud（流式SSE）
- **可视化**：Plotly
- **数据**：JSON + Markdown
- **部署**：Streamlit Community Cloud

## License

MIT
