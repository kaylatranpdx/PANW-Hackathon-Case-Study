import pandas as pd
import streamlit as st

from database import load_entries, save_entry
from nlp import generate_prompt
from summary import generate_weekly_summary
from ai_companion import has_claude

def main():
    st.set_page_config(page_title="AI Journaling Companion", layout="wide")
    st.title("Your Personal Journaling Companion")
    
    tabs = st.tabs(["Daily Journal", "Trends", "Weekly Reflection"])

    with tabs[0]:
        st.subheader("Your Daily Entry")
        recent_entries = load_entries(days=7)
        suggested_prompt = generate_prompt(recent_entries)

        st.markdown("**Your Prompt for Today:**")
        st.info(suggested_prompt)

        text = st.text_area("Write how you're feeling today. Whether it's good or bad, there is no right or wrong way to express yourself: ", height=200)

        if st.button("Save Entry"):
            if text.strip():
                save_entry(text)
                st.success("Your entry has been saved.")
            else:
                st.warning("Think about what you want to write before saving.")

        if recent_entries:
            st.markdown("**Recent Entries:**")
            for entry in reversed(recent_entries[-5:]):
                header = (
                    f"{entry['created_at'][:10]} - "
                    f"{', '.join(entry['themes']) or 'No Themes'} · "
                    f"{entry['sentiment_label']}"
                )
                with st.expander(header):
                    st.markdown("**Full Entry:**")
                    st.write(entry["text"])
                    st.caption(
                        f"Sentiment Score: {entry['sentiment_score']:.2f}"
                        f"({entry['sentiment_label']})"
                    )
    
    with tabs[1]:
        st.subheader("Emotional Trends")
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
        st.subheader("Our Weekly Catch Up")
        week_entries = load_entries(days=7)

        if not week_entries:
            st.info("No entries for the last 7 days, journal for a week to get a summary!")
        else:
            summary_text = generate_weekly_summary(week_entries)
            st.markdown(summary_text)
if __name__ == "__main__":
    main()
