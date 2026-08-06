"""产品推荐引擎 - 基于风险等级匹配理财产品 + 标准普尔四象限配置"""

import json
from pathlib import Path


def load_products(data_path: str = None) -> dict:
    """加载理财产品数据"""
    if data_path is None:
        data_path = Path(__file__).parent.parent / "data" / "products.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_products_by_risk(risk_level: str, products_data: dict = None) -> list:
    """根据投资者风险等级筛选可购买的理财产品

    Args:
        risk_level: C1-C5
        products_data: 产品数据字典

    Returns:
        list: 可购买的产品列表，按风险等级排序
    """
    if products_data is None:
        products_data = load_products()

    investor_types = products_data.get("investor_types", {})
    investor = investor_types.get(risk_level, investor_types.get("C3"))
    risk_range = investor.get("risk_range", "R1-R3")

    if "-" in risk_range:
        min_r, max_r = risk_range.split("-")
    else:
        min_r = max_r = risk_range

    risk_order = {"R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5}
    min_val = risk_order.get(min_r, 1)
    max_val = risk_order.get(max_r, 5)

    matched = []
    for product in products_data["products"]:
        pr = risk_order.get(product["risk_level"], 1)
        if min_val <= pr <= max_val:
            matched.append(product)

    matched.sort(key=lambda x: risk_order.get(x["risk_level"], 1))
    return matched


def get_standard_poor_allocation(risk_level: str, products_data: dict = None) -> dict:
    """获取标准普尔四象限配置方案

    Args:
        risk_level: C1-C5
        products_data: 产品数据

    Returns:
        dict: 四象限配置方案，含比例、描述、推荐产品
    """
    if products_data is None:
        products_data = load_products()

    sp_model = products_data.get("standard_poor_model", {})
    quadrants = sp_model.get("quadrants", [])

    investor_types = products_data.get("investor_types", {})
    investor = investor_types.get(risk_level, investor_types.get("C3"))
    custom_allocation = investor.get("allocation", {})

    result = []
    label_to_key = {
        "要花的钱": "日常",
        "保命的钱": "保障",
        "生钱的钱": "增值",
        "保本升值的钱": "保本",
    }

    for q in quadrants:
        label = q["label"]
        key = label_to_key.get(label, "日常")
        custom_ratio = custom_allocation.get(key, q["ratio"])

        quadrant_products = get_products_by_risk(
            q["risk"] if "-" not in q["risk"] else "R1-R2",
            products_data
        ) if q["risk"] != "保障型" else []

        result.append({
            "name": q["name"],
            "label": label,
            "ratio": custom_ratio,
            "description": q["description"],
            "suggested_products": q["products"],
            "risk": q["risk"],
            "sample_products": [p["name"] for p in quadrant_products[:3]],
        })

    return {"model_name": sp_model.get("name", ""), "quadrants": result}


def get_product_summary(products_data: dict = None) -> dict:
    """获取产品数据统计摘要"""
    if products_data is None:
        products_data = load_products()

    products = products_data["products"]
    total = len(products)

    by_risk = {}
    by_type = {}
    for p in products:
        by_risk[p["risk_level"]] = by_risk.get(p["risk_level"], 0) + 1
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1

    return {
        "total": total,
        "by_risk": dict(sorted(by_risk.items())),
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])),
    }


def recommend_portfolio(risk_level: str, amount: float = 100000, products_data: dict = None) -> dict:
    """生成投资组合建议

    Args:
        risk_level: C1-C5
        amount: 投资金额（元）
        products_data: 产品数据

    Returns:
        dict: 投资组合建议，含四象限分配金额和推荐产品
    """
    if products_data is None:
        products_data = load_products()

    allocation = get_standard_poor_allocation(risk_level, products_data)
    portfolio = []

    for q in allocation["quadrants"]:
        ratio = q["ratio"] / 100
        allocated = amount * ratio
        portfolio.append({
            "quadrant": q["label"],
            "name": q["name"],
            "ratio": q["ratio"],
            "amount": round(allocated, 2),
            "description": q["description"],
            "products": q["suggested_products"],
        })

    return {
        "risk_level": risk_level,
        "total_amount": amount,
        "portfolio": portfolio,
        "model": allocation["model_name"],
    }
