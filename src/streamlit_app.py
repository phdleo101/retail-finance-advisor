"""零售金融智能顾问 - Streamlit 主应用"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from risk_engine import (
    load_questions,
    calculate_score,
    get_risk_distribution,
    get_investor_type_detail,
)
from product_engine import (
    load_products,
    get_products_by_risk,
    get_standard_poor_allocation,
    get_product_summary,
    recommend_portfolio,
)
from rag_engine import query_stream

# ==================== 配置 ====================

st.set_page_config(
    page_title="零售金融智能顾问",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 暗黑模式
def apply_dark_mode(dark: bool):
    if dark:
        st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        .stSidebar { background-color: #161b22; }
        .stMarkdown, .stText, p, span, li { color: #fafafa !important; }
        .stButton > button { background-color: #21262d; color: #fafafa; border-color: #30363d; }
        .stButton > button:hover { background-color: #30363d; border-color: #58a6ff; }
        .stTabs [data-baseweb="tab-list"] { background-color: #161b22; }
        .stTabs [data-baseweb="tab"] { color: #8b949e; }
        .stTabs [aria-selected="true"] { color: #58a6ff !important; }
        .stMetric { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; }
        .stMetric label { color: #8b949e !important; }
        .stMetric value { color: #58a6ff !important; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #e9ecef; }
        </style>
        """, unsafe_allow_html=True)


# 侧边栏
with st.sidebar:
    st.title("💰 零售金融智能顾问")
    st.caption("FDE 作品集 项目三 | 零售金融行业")

    st.divider()

    dark_mode = st.toggle("🌙 暗黑模式", value=True)
    apply_dark_mode(dark_mode)

    st.divider()

    investment_amount = st.number_input(
        "💼 投资金额（元）",
        min_value=10000,
        max_value=10000000,
        value=100000,
        step=10000,
        help="设置您的可投资金额，用于生成资产配置方案"
    )

    st.divider()

    st.markdown("### 📌 关于本系统")
    st.markdown("""
    本系统基于 **FDE 五步方法论** 构建：
    1. 行业速学：零售金融AI现状调研
    2. 痛点定位：理财产品推荐"千人一面"
    3. 方案设计：风险测评+产品匹配+RAG问答
    4. AI驱动构建：Streamlit+Dify RAG
    5. 部署验证：Streamlit Cloud在线Demo

    **合规声明**：本系统仅提供投资参考建议，
    不构成投资建议或理财产品销售。
    投资有风险，入市需谨慎。
    """)

    st.divider()
    st.caption("🔗 更多项目：")
    st.caption("[管道腐蚀AI](https://pipeline-corrosion-ai.streamlit.app/) | [智能分诊Agent](https://yuanqi.tencent.com/webim/#/chat/JcPxWB)")


# ==================== 主内容区 ====================

st.title("💰 零售金融智能顾问")
st.markdown("基于风险测评的智能理财产品推荐与资产配置系统")

# 初始化 session state
if "risk_answers" not in st.session_state:
    st.session_state.risk_answers = [3] * 10
if "risk_result" not in st.session_state:
    st.session_state.risk_result = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 0

tab1, tab2, tab3, tab4 = st.tabs(["📋 风险测评", "🏦 产品推荐", "💬 智能问答", "📊 资产配置"])

# ==================== Tab 1: 风险测评 ====================
with tab1:
    st.header("📋 投资者风险测评")

    st.markdown("完成以下10道题，系统将评估您的风险承受能力并推荐适合的理财产品。")

    questions = load_questions()
    products_data = load_products()

    col_q, col_r = st.columns([3, 2])

    with col_q:
        st.subheader("答题区")
        for i, q in enumerate(questions):
            options = [opt["text"] for opt in q["options"]]
            selected = st.radio(
                f"**Q{i+1}. {q['question']}** *({q['category']})*",
                options,
                index=st.session_state.risk_answers[i],
                key=f"q_{i}",
                horizontal=False,
            )
            st.session_state.risk_answers[i] = options.index(selected)

        if st.button("✅ 提交测评", type="primary", width="stretch"):
            scores = [q["options"][st.session_state.risk_answers[i]]["score"] for i, q in enumerate(questions)]
            st.session_state.risk_result = calculate_score(scores)
            st.session_state.risk_distribution = get_risk_distribution(scores)
            st.success("测评完成！请查看右侧结果。")

    with col_r:
        st.subheader("测评结果")

        if st.session_state.risk_result:
            result = st.session_state.risk_result

            # 风险等级大字显示
            level_colors = {
                "C1": "#27AE60", "C2": "#2ECC71", "C3": "#F39C12",
                "C4": "#E67E22", "C5": "#E74C3C"
            }
            color = level_colors.get(result["risk_level"], "#888")
            st.markdown(f"""
            <div style="text-align:center; padding:20px; border-radius:12px;
                        background:linear-gradient(135deg, {color}22, {color}11);
                        border:2px solid {color}; margin-bottom:15px;">
                <h2 style="color:{color}; margin:0;">{result['risk_level']}</h2>
                <h3 style="margin:5px 0;">{result['risk_name']}</h3>
                <p style="color:#888; margin:0;">得分 {result['total_score']}/{result['max_score']}
                ({result['percentage']}%)</p>
            </div>
            """, unsafe_allow_html=True)

            st.info(result["risk_desc"])

            # 各维度得分
            if "risk_distribution" in st.session_state:
                st.markdown("#### 📊 各维度评分")
                dist = st.session_state.risk_distribution
                fig = go.Figure(data=[
                    go.Bar(
                        x=[d["category"] for d in dist],
                        y=[d["score"] for d in dist],
                        marker_color=[level_colors.get(result["risk_level"], "#888")] * len(dist),
                        text=[f"{d['score']}/5" for d in dist],
                        textposition="outside",
                    )
                ])
                fig.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis=dict(range=[0, 5.5], title="得分"),
                    xaxis=dict(title=""),
                )
                st.plotly_chart(fig, width="stretch")

            st.markdown("---")
            st.markdown(f"**可投资产品范围**：{get_investor_type_detail(result['risk_level'], products_data).get('risk_range', '')}")
            st.markdown("👉 前往「产品推荐」Tab 查看推荐产品")
        else:
            st.info("👈 请完成左侧答题后点击「提交测评」")

# ==================== Tab 2: 产品推荐 ====================
with tab2:
    st.header("🏦 理财产品推荐")

    risk_level = st.session_state.risk_result["risk_level"] if st.session_state.risk_result else "C3"
    risk_name = st.session_state.risk_result["risk_name"] if st.session_state.risk_result else "平衡型（默认）"

    st.markdown(f"**当前风险等级**：`{risk_level} - {risk_name}`")

    if not st.session_state.risk_result:
        st.warning("⚠️ 您还未完成风险测评，当前默认显示 C3（平衡型）可投资产品。请先前往「风险测评」Tab 完成测评。")

    # 产品筛选
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_type = st.selectbox("筛选产品类型", ["全部"] + list(set(p["type"] for p in products_data["products"])))
    with col_f2:
        sort_by = st.selectbox("排序方式", ["风险等级（低→高）", "预期收益（高→低）", "起购金额（低→高）"])

    # 获取推荐产品
    recommended = get_products_by_risk(risk_level, products_data)

    if filter_type != "全部":
        recommended = [p for p in recommended if p["type"] == filter_type]

    if sort_by == "预期收益（高→低）":
        def extract_return(p):
            r = p["expected_return"]
            nums = [float(x) for x in r.replace("%", "").replace("-", " ").replace("+", " ").split() if x.replace(".", "").isdigit()]
            return max(nums) if nums else 0
        recommended.sort(key=extract_return, reverse=True)
    elif sort_by == "起购金额（低→高）":
        recommended.sort(key=lambda p: p["min_amount"])

    st.markdown(f"**共找到 {len(recommended)} 款适合您的产品**")

    # 产品列表
    risk_colors = {
        "R1": "#27AE60", "R2": "#2ECC71", "R3": "#F39C12",
        "R4": "#E67E22", "R5": "#E74C3C"
    }

    for p in recommended:
        color = risk_colors.get(p["risk_level"], "#888")
        with st.container():
            cols = st.columns([3, 1, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**{p['name']}**")
                st.caption(f"{p['features']}")
            with cols[1]:
                st.metric("预期收益", p["expected_return"])
            with cols[2]:
                st.metric("起购金额", f"¥{p['min_amount']:,}")
            with cols[3]:
                st.metric("投资期限", p["term"])
            with cols[4]:
                st.markdown(f"""
                <div style="background:{color}; color:white; padding:4px 12px;
                            border-radius:12px; text-align:center; font-weight:bold;
                            display:inline-block; margin-top:8px;">
                    {p['risk_level']} · {p['type']}
                </div>
                """, unsafe_allow_html=True)
            st.divider()

# ==================== Tab 3: 智能问答 ====================
with tab3:
    st.header("💬 金融智能问答")

    st.markdown("基于 RAG 知识库的金融问答系统，可咨询理财产品、风险等级、资产配置等问题。")

    # 示例问题
    st.markdown("#### 💡 试试这些问题：")
    example_cols = st.columns(2)
    examples = [
        "理财产品风险等级有哪些？",
        "什么是标准普尔四象限配置？",
        "货币基金和债券基金有什么区别？",
        "C3平衡型投资者适合什么产品？",
    ]
    for i, ex in enumerate(examples):
        with example_cols[i % 2]:
            if st.button(ex, key=f"example_{i}", width="stretch"):
                st.session_state["chat_input"] = ex

    st.divider()

    # 问答区
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("请输入您的金融问题...", key="chat_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("检索知识库中..."):
                response_placeholder = st.empty()
                full_response = ""
                for chunk in query_stream(user_input):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# ==================== Tab 4: 资产配置 ====================
with tab4:
    st.header("📊 资产配置方案")

    risk_level = st.session_state.risk_result["risk_level"] if st.session_state.risk_result else "C3"
    risk_name = st.session_state.risk_result["risk_name"] if st.session_state.risk_result else "平衡型（默认）"

    st.markdown(f"**当前风险等级**：`{risk_level} - {risk_name}` | **投资金额**：`¥{investment_amount:,.0f}`")

    if not st.session_state.risk_result:
        st.warning("⚠️ 您还未完成风险测评，当前默认使用 C3（平衡型）配置方案。")

    # 标准普尔四象限
    allocation = get_standard_poor_allocation(risk_level, products_data)
    portfolio = recommend_portfolio(risk_level, investment_amount, products_data)

    st.subheader("🏘️ 标准普尔四象限配置")

    # 四象限可视化
    quad_colors = ["#3498DB", "#E74C3C", "#2ECC71", "#F39C12"]
    quad_labels = [q["label"] for q in allocation["quadrants"]]
    quad_ratios = [q["ratio"] for q in allocation["quadrants"]]
    quad_amounts = [p["amount"] for p in portfolio["portfolio"]]

    col_chart, col_detail = st.columns([1, 1])

    with col_chart:
        fig = go.Figure(data=[go.Pie(
            labels=quad_labels,
            values=quad_ratios,
            hole=0.4,
            marker=dict(colors=quad_colors),
            textinfo="label+percent",
            textposition="outside",
        )])
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig, width="stretch")

    with col_detail:
        for i, (q, p) in enumerate(zip(allocation["quadrants"], portfolio["portfolio"])):
            color = quad_colors[i]
            st.markdown(f"""
            <div style="border-left:4px solid {color}; padding:8px 12px; margin-bottom:8px;
                        background:{color}11; border-radius:0 8px 8px 0;">
                <strong style="color:{color};">{q['label']}</strong>
                <span style="float:right; font-weight:bold;">{q['ratio']}% = ¥{p['amount']:,.0f}</span>
                <br><small>{q['description']}</small>
                <br><small>推荐产品：{q['suggested_products']}</small>
            </div>
            """, unsafe_allow_html=True)

    # 投资组合详情
    st.subheader("💼 投资组合详情")

    portfolio_df = pd.DataFrame([
        {
            "象限": p["quadrant"],
            "账户名称": p["name"],
            "配置比例": f"{p['ratio']}%",
            "分配金额": f"¥{p['amount']:,.2f}",
            "说明": p["description"],
            "推荐产品": p["products"],
        }
        for p in portfolio["portfolio"]
    ])
    st.dataframe(portfolio_df, width="stretch", hide_index=True)

    # 产品数据统计
    st.subheader("📈 产品库统计")
    summary = get_product_summary(products_data)

    cols = st.columns(4)
    with cols[0]:
        st.metric("产品总数", f"{summary['total']} 款")
    with cols[1]:
        st.metric("风险等级", f"{len(summary['by_risk'])} 级")
    with cols[2]:
        st.metric("产品类型", f"{len(summary['by_type'])} 类")
    with cols[3]:
        st.metric("覆盖范围", "R1-R5 全覆盖")

    # 风险等级分布图
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("#### 按风险等级分布")
        risk_df = pd.DataFrame(list(summary["by_risk"].items()), columns=["风险等级", "数量"])
        fig_risk = px.bar(risk_df, x="风险等级", y="数量", color="风险等级",
                          color_discrete_map=risk_colors, height=300)
        fig_risk.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_risk, width="stretch")

    with col_d2:
        st.markdown("#### 按产品类型分布")
        type_df = pd.DataFrame(list(summary["by_type"].items()), columns=["类型", "数量"])
        fig_type = px.pie(type_df, names="类型", values="数量", height=300, hole=0.4)
        fig_type.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_type, width="stretch")

    st.divider()
    st.caption("📊 配置方案基于标准普尔家庭资产配置模型，实际投资请咨询专业理财顾问。")
    st.caption("🔗 本系统为 FDE 作品集项目三，仅展示技术能力，不构成投资建议。")
