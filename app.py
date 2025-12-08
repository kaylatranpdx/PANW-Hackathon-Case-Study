# this file is the main ui app file, using streamlit
#each part of main is separated by tabs: Daily Journal, Trends, Weekly Reflection
import pandas as pd
import streamlit as st

from database import load_entries, save_entry
from nlp import generate_prompt
from summary import generate_weekly_summary
from ai_companion import has_claude, generate_companion_response

st.set_page_config(
    page_title="AI Journaling Companion",
    page_icon="🌊",
    layout="wide",
)

with open("themes.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    st.markdown("<div class='hero-title'>Your Personal Journaling Companion</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-title'>🫂</div>", unsafe_allow_html=True)
    tabs = st.tabs(["Daily Journal", "Trends", "Weekly Reflection"])

    with tabs[0]:
        recent_entries = load_entries(days=7)
        suggested_prompt = generate_prompt(recent_entries)

        st.markdown("<div class='prompt-heading'>Your Companion asks...</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prompt-text'>{suggested_prompt}</div>", unsafe_allow_html=True)

        text = st.text_area(
            "Journal Entry",
            placeholder="Write how you're feeling today. Whether it's good or bad, this is your safe space.",
            height=200,
            label_visibility="collapsed",
        )

        if st.button("Save Entry"):
            if not text.strip():
                st.warning("Think about what you want to write before saving.")
            else:
                entry_data = {"text": text}
                ai_reply = generate_companion_response(entry_data)
                save_entry(text, prompt=suggested_prompt, ai_reply=ai_reply)
                
                st.success("Your entry has been saved.")

                if ai_reply:
                    st.markdown("### Your Companion says:")
                    st.markdown(f"<div class='entry-response'>{ai_reply}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("*Your companion is listening quietly with you.*")

        recent_entries = load_entries(days=7)
        with st.sidebar:
            st.markdown("<div class='sidebar-heading'>Recent Entries</div>", unsafe_allow_html=True)

            if recent_entries:
                for entry in reversed(recent_entries):
                    themes_raw = entry.get("themes", []) or []
                    if isinstance(themes_raw, str):
                        themes_list = [themes_raw]
                    else:
                        try:
                            themes_list = list(themes_raw)
                        except TypeError:
                            themes_list = []

                    themes_display = ", ".join(str(t).strip() for t in themes_list if t) or "No themes"

                    sentiment = entry.get("sentiment_label") or "neutral"
                    sentiment_display = str(sentiment).title()

                    header = f"{entry['created_at'][:10]} — {themes_display} · {sentiment_display}"

                    with st.expander(header):
                        if entry.get("prompt"):
                            st.markdown("**Prompt:**")
                            st.markdown(f"<div class='prompt-box'>{entry['prompt']}</div>", unsafe_allow_html=True)

                        st.markdown("**Your Entry:**")
                        st.markdown(f"<div class='entry-response'>{entry['text']}</div>", unsafe_allow_html=True)

                        if entry.get("ai_reply"):
                            st.markdown("**Companion's Response:**")
                            st.markdown(f"<div class='entry-response'>{entry['ai_reply']}</div>", unsafe_allow_html=True)        
    
    with tabs[1]:
        st.markdown("<div class='tab-heading'>Your Emotional Trends</div>", unsafe_allow_html=True)
        entries = load_entries()
        if not entries:
            st.info("No entries yet, start journaling to see your shift in emotions over time.")
        else:
            df = pd.DataFrame(entries)
            df["created_datetime"] = pd.to_datetime(
                df["created_at"],
                utc=True,
                errors="coerce",
            )
            df["created_date"] = df["created_datetime"].dt.date

            daily_sentiment = (
                df.groupby("created_date")["sentiment_score"]
                .mean()
                .reset_index()
                .sort_values("created_date")
            )

            st.markdown("**Average Daily Sentiment Over Time**")
            st.line_chart(
                daily_sentiment.set_index("created_date")["sentiment_score"],
                height=300,
            )

            all_themes: list[str] = []
            for theme in df["themes"]:
                all_themes.extend(theme)

            if all_themes:
                theme_count = (
                    pd.Series(all_themes)
                    .value_counts()
                    .rename_axis("theme")
                    .reset_index(name="count")
                )

                st.markdown("**Most Frequent Themes**")
                st.bar_chart(
                    theme_count.set_index("theme")["count"],
                    height=300,
                )

    with tabs[2]:
        st.markdown("<div class='tab-heading'>Our Weekly Catch Up</div>", unsafe_allow_html=True)
        week_entries = load_entries(days=7)

        if not week_entries:
            st.info("No entries for the last 7 days, journal for a week to get a summary!")
        else:
            summary_text = generate_weekly_summary(week_entries)
            st.markdown(summary_text)

if __name__ == "__main__":
    main()
