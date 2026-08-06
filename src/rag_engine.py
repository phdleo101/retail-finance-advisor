"""RAG 引擎 - Dify Cloud 流式问答 + 本地降级"""

import json
import time
import requests
from pathlib import Path


def _load_kb_content() -> str:
    """加载本地知识库内容作为降级方案"""
    kb_path = Path(__file__).parent.parent / "data" / "knowledge" / "finance_kb.md"
    if kb_path.exists():
        with open(kb_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


KB_CONTENT = _load_kb_content()


def _load_dify_config():
    """从 Streamlit Secrets 读取 Dify 配置

    兼容两种 URL 格式：
    - 基础 URL: https://api.dify.ai/v1 （推荐，代码自动追加 /chat-messages）
    - 完整 URL: https://api.dify.ai/v1/chat-messages （自动去除尾部 /chat-messages）
    """
    try:
        import streamlit as st
        if "dify" in st.secrets:
            api_url = st.secrets["dify"].get("api_url", "")
            # 兼容旧配置：如果 URL 已包含 /chat-messages，去除尾部
            if api_url.endswith("/chat-messages"):
                api_url = api_url[: -len("/chat-messages")]
            return {
                "api_url": api_url,
                "api_key": st.secrets["dify"].get("api_key", ""),
            }
    except Exception:
        pass
    return {"api_url": "", "api_key": ""}


def _query_dify_blocking(query: str) -> str:
    """阻塞式查询 Dify API"""
    config = _load_dify_config()
    if not config["api_url"] or not config["api_key"]:
        return _local_fallback(query)

    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "user": "finance-advisor-user",
    }
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }

    for attempt in range(3):
        try:
            response = requests.post(
                f"{config['api_url']}/chat-messages",
                headers=headers,
                json=payload,
                timeout=(10, 90),
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("answer", "")
            else:
                time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)

    return _local_fallback(query)


def _query_dify_stream(query: str):
    """流式查询 Dify API (SSE)"""
    config = _load_dify_config()
    if not config["api_url"] or not config["api_key"]:
        yield _local_fallback(query)
        return

    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "user": "finance-advisor-user",
    }
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }

    for attempt in range(3):
        try:
            response = requests.post(
                f"{config['api_url']}/chat-messages",
                headers=headers,
                json=payload,
                timeout=(10, 90),
                stream=True,
            )
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode("utf-8")
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            try:
                                data = json.loads(data_str)
                                if data.get("event") == "message":
                                    yield data.get("answer", "")
                                elif data.get("event") == "message_end":
                                    return
                            except json.JSONDecodeError:
                                continue
                return
            else:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
        except Exception:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue

    yield _local_fallback(query)


def _local_fallback(query: str) -> str:
    """本地知识库降级方案"""
    query_lower = query.lower()

    if any(kw in query_lower for kw in ["风险等级", "r1", "r2", "r3", "r4", "r5", "风险类型"]):
        return """**理财产品风险等级说明**

| 等级 | 名称 | 特点 | 收益范围 |
|---|---|---|---|
| R1 | 低风险 | 保本保息，流动性高 | 0.25%-2.5% |
| R2 | 中低风险 | 本金较安全，波动小 | 2.5%-5% |
| R3 | 中风险 | 收益与波动适中 | 4%-10% |
| R4 | 中高风险 | 追求较高收益，波动大 | 8%-20% |
| R5 | 高风险 | 波动剧烈，可能大幅亏损 | 15%-35%+ |

投资者分为C1-C5五级，只能购买对应风险等级及以下的产品。

> 注：当前为本地知识库模式（Dify API 未配置），完整智能问答需配置 Dify API。"""

    elif any(kw in query_lower for kw in ["标准普尔", "标普", "四象限", "资产配置", "配置"]):
        return """**标准普尔家庭资产配置四象限**

| 象限 | 名称 | 比例 | 用途 | 产品 |
|---|---|---|---|---|
| 第一 | 要花的钱 | 10% | 3-6个月日常开销 | 活期、货币基金 |
| 第二 | 保命的钱 | 20% | 意外重疾保障 | 保险 |
| 第三 | 生钱的钱 | 30% | 追求高收益 | 股票/指数基金 |
| 第四 | 保本升值的钱 | 40% | 养老/教育金 | 国债、年金险 |

> 注：当前为本地知识库模式，完整智能问答需配置 Dify API。"""

    elif any(kw in query_lower for kw in ["基金", "货币基金", "债券基金", "股票基金", "指数基金"]):
        return """**基金类型说明**

- **货币基金**：投资短期货币工具，T+0/T+1赎回，年化1.5-2.5%，适合零钱理财
- **债券基金**：纯债波动小（2.5-5%），可转债波动大（5-10%）
- **混合基金**：股债混合，偏债型/平衡型/偏股型，收益4-12%
- **股票基金**：80%以上投股票，收益8-20%，波动大
- **指数基金**：被动跟踪指数，费率低，透明度高
- **ETF**：场内交易，T+0（跨境），流动性好
- **QDII**：投资海外市场，分散单一市场风险

> 注：当前为本地知识库模式，完整智能问答需配置 Dify API。"""

    elif any(kw in query_lower for kw in ["存款", "大额存单", "定期", "国债"]):
        return """**存款与债券类产品**

- **活期存款**：随时存取，0.25%，适合日常管理
- **定期存款**：3个月-5年，1.15%-1.95%，提前支取按活期计息
- **大额存单**：20万起存，利率高于定期，可转让，存款保险保障
- **储蓄国债**：国家信用担保，免利息税，3年2.18%/5年2.30%
- **国债逆回购**：以国债为抵押，安全性极高，月末季末收益飙升

存款保险制度：单家银行50万以内全额保障。

> 注：当前为本地知识库模式，完整智能问答需配置 Dify API。"""

    else:
        return f"""您问的是：「{query}」

我目前的本地知识库可以回答以下话题：
1. 理财产品风险等级（R1-R5）
2. 投资者风险类型（C1-C5）
3. 标准普尔四象限资产配置
4. 各类理财产品介绍（存款/基金/理财/保险）
5. 投资常见误区

请尝试以上话题，或配置 Dify API 获取更完整的智能问答体验。

> 注：当前为本地知识库模式（Dify API 未配置）。"""


def query_stream(query: str):
    """流式查询入口（生成器）"""
    yield from _query_dify_stream(query)
