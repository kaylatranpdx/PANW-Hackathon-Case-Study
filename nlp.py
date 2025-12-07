from typing import List, Dict, Tuple
from transformers import pipeline
from ai_companion import has_claude, call_companion

_sentiment_pipe = None

def get_sentiment_pipeline():
    global _sentiment_pipe
    if _sentiment_pipe is None:
        _sentiment_pipe = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )
    return _sentiment_pipe

def compute_sentiment(text: str) -> Dict[float, str]:
    if not text.strip():
        return 0.0, "neutral"
    
    pipe = get_sentiment_pipeline()
    result = pipe(text[:512])[0]
    label = result["label"].upper()
    score = float(result["score"])

    if label == "POSITIVE":
        normal = score
        sentiment_label = "positive"

    elif label == "NEGATIVE":
        normal = -score
        sentiment_label = "negative"

    if abs(normal) < 0.2:
        normal = 0.0
        sentiment_label = "neutral"

    return normal, sentiment_label

THEME_KEYWORDS: Dict[str, List[str]] = {
    "Work": ["work", "job", "career", "office", "boss", "colleague", "project", "meeting", "deadline", "email"],
    "Family": ["family", "mother", "father", "sister", "brother", "child", "parent", "home", "relatives", "household"],
    "Health": ["health", "doctor", "medicine", "illness", "exercise", "diet", "fitness", "wellness", "hospital", "treatment", "walk", "run"],
    "Finance": ["money", "finance", "budget", "expense", "income", "savings", "investment", "debt", "bills", "payment"],
    "Friends": ["friend", "friends", "hangout", "social", "party"],
    "Mood": ["happy", "sad", "angry", "excited", "depressed", "anxious", "joyful", "frustrated", "content", "bored", "calm", "lonely", "stressed"],
}

def extract_themes(text: str) -> List[str]:
    tokens = set(text.lower().split())
    themes: List[str] = []

    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in tokens for keyword in keywords):
            themes.append(theme)

    return themes or ["General"]

def generate_prompt_rule(last_entries: List[Dict]) -> str:
    if not last_entries:
        return "What is one thing on your mind right now?"
    
    last = last_entries[-1]
    themes = last.get("themes", [])
    sentiment_label = last.get("sentiment_label", "neutral")

    if "Work" in themes:
        return "Work has been on your mind lately. How are you feeling about your job or career?"
    
    if sentiment_label == "negative":
        return "You seem to be having a heavy heart as of late. What is one small thing that brought you even a bit of joy today?"
    
    if sentiment_label == "positive":
        return "You seem to be in a good mood lately. What is one thing that made you smile recently?"
    
    return "Let's take a deep breath and pause. What is the strongest feeling you feel right now?"

def generate_prompt_companion(last_entries: List[Dict]) -> str:
    if not has_claude():
        return generate_prompt_rule(last_entries)
    
    if not last_entries:
        context = "The user is starting journaling and may have blank page anxiety."

    else:
        bullets = []
        for entry in last_entries[-3:]:
            bullets.append(
                f"- {entry['created at'][:10]}: mood{entry['sentiment_label']}, "
                f"themes: {', '.join(entry['themes'])}"
            )

        context = "Recent entries: \n" + "\n".join(bullets)
    user_prompt = (
        context
        + "\n\nBased on this, suggest ONE gentle journaling prompt (<= 30 words) "
        "that helps the user reflect today. Do not give advice or try to solve problems, just suggest a prompt."
    )
    response = call_companion(user_prompt)
    if response:
        return response
    
    return generate_prompt_rule(last_entries)

def generate_prompt(last_entries: List[Dict]) -> str:
    if has_claude():
        return generate_prompt_companion(last_entries)
    return generate_prompt_rule(last_entries)
        
        