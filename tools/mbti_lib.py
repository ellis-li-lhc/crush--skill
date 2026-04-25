#!/usr/bin/env python3
"""
MBTI 恋爱匹配库
16型人格恋爱兼容性评分
"""

MATCHING_MATRIX = {
    "INTJ": {
        "best": ["ENFP", "ENTP"],
        "great": ["INFJ", "INTP", "ENTJ"],
        "good": ["INFP", "ENFJ"],
        "ok": ["ISTJ", "ISFJ"],
        "avoid": ["ESFJ", "ESTJ", "ESFP"]
    },
    "INTP": {
        "best": ["ENTJ", "INFJ", "INTJ"],
        "great": ["ENTP", "ENFP", "INFP"],
        "good": ["ISTP", "ESTP"],
        "ok": ["ISTJ", "ISFJ"],
        "avoid": ["ESFJ", "ESTJ"]
    },
    "ENTJ": {
        "best": ["INTP", "INFJ", "ENTP"],
        "great": ["INTJ", "ENFP"],
        "good": ["ENTJ", "ESTJ", "ENFJ"],
        "ok": ["ISTJ", "ISFJ"],
        "avoid": ["ISFP", "ESFP"]
    },
    "ENTP": {
        "best": ["INFJ", "INTP", "ENFP"],
        "great": ["INTJ", "ENTJ", "INFP"],
        "good": ["ESTP", "ESFP"],
        "ok": ["INTP", "ENTP"],
        "avoid": ["ISTJ", "ISFJ", "ESTJ"]
    },
    "INFJ": {
        "best": ["ENFP", "ENTP"],
        "great": ["INTP", "INTJ", "ENFJ"],
        "good": ["INFP", "ENTJ"],
        "ok": ["INFJ", "ISFJ"],
        "avoid": ["ESTP", "ESTJ", "ESFP"]
    },
    "INFP": {
        "best": ["ENFJ", "INFJ", "ENFP"],
        "great": ["INTJ", "ENTP", "INFP"],
        "good": ["ISFJ", "ESFJ"],
        "ok": ["INTP", "ENTP"],
        "avoid": ["ESTJ", "ESTP", "ISTJ"]
    },
    "ENFJ": {
        "best": ["INFP", "ENFP", "ISFJ"],
        "great": ["INFJ", "INTP"],
        "good": ["ENTJ", "ESTJ", "ENFJ"],
        "ok": ["ISFJ", "ESFJ"],
        "avoid": ["ESTP", "ISTP"]
    },
    "ENFP": {
        "best": ["INFJ", "INTJ"],
        "great": ["ENFJ", "ENTP", "INFP"],
        "good": ["INTP", "ENTJ", "ENFP"],
        "ok": ["ISFJ", "ESFJ"],
        "avoid": ["ISTJ", "ESTJ", "ISTP"]
    },
    "ISTJ": {
        "best": ["ESFP", "ESTP", "ISFJ"],
        "great": ["ISTP", "ESFJ", "ESTJ"],
        "good": ["INTJ", "INTP"],
        "ok": ["INFJ", "INFP"],
        "avoid": ["ENFP", "ENTP", "ENTJ"]
    },
    "ISFJ": {
        "best": ["ESFP", "ESTP"],
        "great": ["ISFJ", "ESFJ", "ENFJ"],
        "good": ["INFJ", "INTP"],
        "ok": ["INTJ", "ISTJ"],
        "avoid": ["ENTP", "ENTJ"]
    },
    "ESTJ": {
        "best": ["INTP", "ISTP"],
        "great": ["ISTJ", "ISFJ", "ENTJ"],
        "good": ["ESTJ", "ESFJ"],
        "ok": ["INFP", "ENFP"],
        "avoid": ["ENFP", "INFP", "ENTP"]
    },
    "ESFJ": {
        "best": ["ISFP", "ISTP"],
        "great": ["ISFJ", "ESFJ", "ESTP"],
        "good": ["INFJ", "ENFJ"],
        "ok": ["INTJ", "ENTJ"],
        "avoid": ["INTJ", "ENTJ", "INTP"]
    },
    "ISTP": {
        "best": ["ESTJ", "ENTJ"],
        "great": ["ISTP", "ESTP", "ISFP"],
        "good": ["INTP", "ENTP"],
        "ok": ["INTJ", "INFJ"],
        "avoid": ["ENFJ", "INFJ", "ENTJ"]
    },
    "ISFP": {
        "best": ["ENFJ", "ESTJ", "ENTJ"],
        "great": ["ISFP", "ESFP", "INFP"],
        "good": ["ISTP", "INTP"],
        "ok": ["INTJ", "ENTJ"],
        "avoid": ["ENTJ", "INTJ", "ESTJ"]
    },
    "ESTP": {
        "best": ["ISFJ", "ISTJ"],
        "great": ["ESTP", "ESFP", "ISTP"],
        "good": ["INTP", "ENTP"],
        "ok": ["INFJ", "INTJ"],
        "avoid": ["INFJ", "INTJ", "ENFJ"]
    },
    "ESFP": {
        "best": ["ISFJ", "ISTJ"],
        "great": ["ESFP", "ESTP", "ISFP"],
        "good": ["ENFP", "ENTP"],
        "ok": ["INTP", "ENTP"],
        "avoid": ["INTJ", "INFJ", "ENTJ"]
    }
}

SCORES = {
    "best": 95,
    "great": 85,
    "good": 75,
    "ok": 65,
    "avoid": 45
}

STYLE_DESCRIPTIONS = {
    "INTJ": {
        "name": "建筑师",
        "love_style": "理性但一旦认定会很深情，会规划未来，不太会表达感情但心里有你",
        "strength": "有规划、靠谱、专一",
        "weakness": "不解风情、不会哄人"
    },
    "INTP": {
        "name": "逻辑学家",
        "love_style": "理性分析感情，需要独处时间，但会认真对待",
        "strength": "聪明、诚实、尊重对方",
        "weakness": "冷漠、不浪漫"
    },
    "ENTJ": {
        "name": "指挥官",
        "love_style": "主动出击，掌控欲强但会照顾人",
        "strength": "有主见、能力强、保护欲强",
        "weakness": "太强势、不够温柔"
    },
    "ENTP": {
        "name": "辩论家",
        "love_style": "聪明有趣，聊天永远不会无聊，喜欢挑战",
        "strength": "幽默、聪明、话题多",
        "weakness": "太爱争辩、不够专一"
    },
    "INFJ": {
        "name": "提倡者",
        "love_style": "深情专一懂你，会默默付出",
        "strength": "温柔、懂你、痴情",
        "weakness": "太被动、容易受伤"
    },
    "INFP": {
        "name": "调停者",
        "love_style": "浪漫主义，会为了你做任何事",
        "strength": "浪漫、温柔、忠诚",
        "weakness": "太敏感、容易想多"
    },
    "ENFJ": {
        "name": "主人公",
        "love_style": "热情主动，照顾人无微不至",
        "strength": "温暖、照顾人、鼓励你",
        "weakness": "控制欲强、太粘人"
    },
    "ENFP": {
        "name": "竞选者",
        "love_style": "热情似火，创意无限，恋爱体验感拉满",
        "strength": "有趣、热情、创意多",
        "weakness": "��分钟热度、容易变心"
    },
    "ISTJ": {
        "name": "物流师",
        "love_style": "稳重可靠，默默做事不爱表达",
        "strength": "靠谱、负责、忠诚",
        "weakness": "无趣、不浪漫"
    },
    "ISFJ": {
        "name": "守护者",
        "love_style": "温柔照顾，默默守护你",
        "strength": "温柔、体贴、照顾人",
        "weakness": "太被动、不敢表达"
    },
    "ESTJ": {
        "name": "总经理",
        "love_style": "强势保护，会帮你安排好一切",
        "strength": "有能力、靠谱、决策力强",
        "weakness": "太强势、大男子主义"
    },
    "ESFJ": {
        "name": "执行官",
        "love_style": "社交达人，friends带给你，关心你的朋友",
        "strength": "外向、照顾人、人缘好",
        "weakness": "太八卦、管制多"
    },
    "ISTP": {
        "name": "鉴赏家",
        "love_style": "动手能力强，浪漫在于行动",
        "strength": "动手能力强、稳重",
        "weakness": "太冷漠、不表达"
    },
    "ISFP": {
        "name": "艺术家",
        "love_style": "浪漫敏感，会用艺术方式表达爱",
        "strength": "浪漫、有才、温柔",
        "weakness": "太敏感、情绪化"
    },
    "ESTP": {
        "name": "企业家",
        "love_style": "刺激好玩，带你体验各种新鲜事物",
        "strength": "有趣、胆大、社交强",
        "weakness": "花心、不靠谱"
    },
    "ESFP": {
        "name": "表演者",
        "love_style": "活在当下，及时行乐，开心最重要",
        "strength": "开心果、有趣、热情",
        "weakness": "没规划、太冲动"
    }
}


def get_compatibility(user_mbti: str, target_mbti: str) -> dict:
    """
    获取两个MBTI类型的匹配度
    """
    if user_mbti not in MATCHING_MATRIX:
        return {"score": 50, "level": "unknown", "description": "未知的MBTI类型"}

    matrix = MATCHING_MATRIX[user_mbti]

    for level, types in matrix.items():
        if target_mbti in types:
            score = SCORES[level]
            break
    else:
        score = 50
        level = "ok"

    style = STYLE_DESCRIPTIONS.get(target_mbti, {})

    return {
        "score": score,
        "level": level,
        "name": style.get("name", target_mbti),
        "love_style": style.get("love_style", ""),
        "strength": style.get("strength", ""),
        "weakness": style.get("weakness", "")
    }


def recommend_types(user_mbti: str, limit: int = 3) -> list:
    """
    推荐最适合的恋爱对象类型
    """
    if user_mbti not in MATCHING_MATRIX:
        return []

    matrix = MATCHING_MATRIX[user_mbti]
    results = []

    for level in ["best", "great", "good"]:
        for mbti in matrix.get(level, []):
            results.append({
                "mbti": mbti,
                "level": level,
                **get_compatibility(user_mbti, mbti)
            })
            if len(results) >= limit:
                return results

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mbti_lib.py <your_mbti> [limit]")
        sys.exit(1)

    your_mbti = sys.argv[1].upper()
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    results = recommend_types(your_mbti, limit)

    for i, r in enumerate(results, 1):
        print(f"{i}. {r['mbti']} ({r['name']}) - {r['score']}%")
        print(f"   恋爱风格: {r['love_style']}")
        print(f"   优势: {r['strength']}")
        print(f"   注意点: {r['weakness']}")
        print()