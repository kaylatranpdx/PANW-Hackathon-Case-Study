from collections import Counter
from typing import List, Dict
from ai_companion import has_claude, call_companion

def generate_weekly_summary_rule(entries: List[Dict]) -> str:
    if not entries:
        return (
            "You don't have any entries this week yet. "
            "Try starting with a small reflection of your day."
        )
    
    theme_counter: Counter[str] = Counter()
    sentiments: list[float] = []
    theme_sentiments: Dict[str, List[float]] = {}

    for entry in entries:
        themes = entry["themes"]
        sentiments_score = entry["sentiment_score"]
        sentiments.append(sentiments_score)
        for theme in themes:
            theme_counter[theme] += 1
            theme_sentiments.setdefault(theme, []).append(sentiments_score)

    total_entries = len(entries)
    avg_sentiment = sum(sentiments) / total_entries if total_entries > 0 else 0.0

    common_themes = [theme for theme, _ in theme_counter.most_common(3)]
    lines: List[str] = []

    lines.append(f"This week, you made {total_entries} journal entries.")
    if common_themes:
        lines.append(f"You wrote most about: " + ", ".join(common_themes) + ".")

    best_theme = None
    best_theme_score = None

    for theme, scores in theme_sentiments.items():
        average_score = sum(scores) / len(scores)
        if best_theme_score is None or average_score > best_theme_score:
            best_theme_score = average_score
            best_theme = theme

    if best_theme is not None and best_theme_score is not None and best_theme_score > avg_sentiment:
        lines.append(
            f"Your mood seemed to be brighter when writing about {best_theme}."
        )

    worst_theme = None
    worst_theme_score = None
    for theme, scores in theme_sentiments.items():
        average_score = sum(scores) / len(scores)
        if worst_theme_score is None or average_score < worst_theme_score:
            worst_theme_score = average_score
            worst_theme = theme

    if worst_theme is not None and worst_theme_score is not None and worst_theme_score < avg_sentiment:
        lines.append(
            f"You seemed to struggle more when writing about {worst_theme}. "
            "This might be an area to explore further later."
        )

    lines.append(
        "As you continue to write, consider reflecting on what themes keep you grounded and bring you joy."
    )

    return "\n\n".join(lines)

def generate_weekly_summary_companion(entries: List[Dict]) -> str:
    if not entries:
        return (
            "You don't have any entries this week yet. "
            "Try starting with a small reflection of your day."
        )
    
    bullets = []
    for entry in entries[-10:]:
        bullets.append(
            f"- {entry['created at'][:10]}: mood{entry['sentiment_label']}, "
            f"themes: {', '.join(entry['themes'])}"
        )
    user_prompt = (
        "Here are the user's journal entries for the week:\n"
        + "\n".join(bullets)
        + "\n\nBased on these entries, provide a thoughtful weekly summary "
        "that reflects on their themes and emotional journey. "
        "Keep it warm, encouraging, and validating, and under 3 short paragraphs."
    )

    response = call_companion(user_prompt, max_tokens=300)
    if response:
        return response
    
    return generate_weekly_summary_rule(entries)

def generate_weekly_summary(entries: List[Dict]) -> str:
    if has_claude():
        return generate_weekly_summary_companion(entries)
    return generate_weekly_summary_rule(entries)