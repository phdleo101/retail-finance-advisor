"""风险评分引擎 - 基于投资者风险测评问卷计算风险等级"""

import json
from pathlib import Path


def load_questions(data_path: str = None) -> list:
    """加载风险测评题库"""
    if data_path is None:
        data_path = Path(__file__).parent.parent / "data" / "risk_questions.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]


def calculate_score(answers: list) -> dict:
    """计算风险测评得分并返回风险等级

    Args:
        answers: 每题的选项分数列表，如 [5, 3, 2, 3, 3, 3, 4, 4, 3, 3]

    Returns:
        dict: 包含总分、风险等级、风险类型名称、描述
    """
    total_score = sum(answers)
    max_score = len(answers) * 5
    percentage = (total_score / max_score) * 100

    if total_score <= 18:
        risk_level = "C1"
        risk_name = "保守型"
        risk_desc = "追求保本保息，不能接受任何亏损。建议以存款和货币基金为主。"
    elif total_score <= 30:
        risk_level = "C2"
        risk_name = "稳健型"
        risk_desc = "追求稳健收益，可接受极小幅波动。建议以债券类和银行理财R2为主。"
    elif total_score <= 38:
        risk_level = "C3"
        risk_name = "平衡型"
        risk_desc = "追求收益与风险的平衡。建议股债均衡配置，混合基金为核心。"
    elif total_score <= 45:
        risk_level = "C4"
        risk_name = "进取型"
        risk_desc = "追求较高收益，可承受较大波动。建议以权益类资产为主，指数基金+股票基金为核心。"
    else:
        risk_level = "C5"
        risk_name = "激进型"
        risk_desc = "追求高收益，可承受大幅亏损。可配置行业主题基金和私募基金等高风险产品。"

    return {
        "total_score": total_score,
        "max_score": max_score,
        "percentage": round(percentage, 1),
        "risk_level": risk_level,
        "risk_name": risk_name,
        "risk_desc": risk_desc,
    }


def get_risk_distribution(answers: list) -> list:
    """获取各维度得分分布用于可视化"""
    questions = load_questions()
    distribution = []
    for i, (q, score) in enumerate(zip(questions, answers)):
        distribution.append({
            "category": q["category"],
            "score": score,
            "max_score": 5,
            "percentage": (score / 5) * 100,
        })
    return distribution


def get_investor_type_detail(risk_level: str, products_data: dict) -> dict:
    """获取投资者类型的详细配置建议"""
    investor_types = products_data.get("investor_types", {})
    if risk_level in investor_types:
        return investor_types[risk_level]
    return investor_types.get("C3", {})
