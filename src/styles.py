"""UI 样式配置 - 暗黑/明亮模式 CSS 常量"""

DARK_MODE_CSS = """
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
"""

LIGHT_MODE_CSS = """
<style>
.stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #e9ecef; }
</style>
"""


def apply_theme(dark: bool):
    """应用暗黑/明亮模式样式"""
    import streamlit as st
    st.markdown(DARK_MODE_CSS if dark else LIGHT_MODE_CSS, unsafe_allow_html=True)
