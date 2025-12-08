# AI Journaling Companion Design Document

## Problem Overview
Journaling is a useful tool for individuals that want better emotional wellness. However, for some cases, there are people that struggle when they're journaling. Those struggles can come from "blank page" anxiety where they aren't sure what to write, or having the ability to write but cannot seem to identify any patterns in their writing. These struggles can stunt a person's emotional growth and hinder their wellness.

## Solution Summary
This AI Powered Journaling Companion transforms journaling into a reflective conversation.

It has the ability to:
- Provide gentle prompts to the user, using the context of the user's previous entries as a guide.
- Analyzes the sentiment and prominent themes in each journal entry.
- Responds to each journal entry with warm and compassionate reflections.
- Creates visualizations of the user's emotional trends on a weekly basis, using sentiments and themes from the user's entries.
- Generates a thoughtful summary of the user's past week, highlighting the user's positive emotions, and acknowledging their negative emotions.

## Target Demographic
The AI Journaling Companion is meant for: 
- Users that want to journal but have no idea how to start and needs some encouragement.
- Users that want a better understanding of their emotional patterns.
- Users that are busy with work or school and don't have the time to sit down and write on a paper.

## Key Features Implemented
- Dynamic AI journal prompts, analyzing theme and sentiment from previous entries
- Dynamic AI responses to each journal entry that a user makes
- Sentiment and theme detection, NLP extracts emotional tone and topics
- Local and privacy database storage to ensure privacy using SQLite
- Ocean water-like UI, promotes calmness
- Emotional Trends tab, provides graph visualizations of the user's emotional trends and average sentiment over the week
- Recent Entries sidebar, shows the user the prompt that was asked and their corresponding entry.

## Architecture
    Companion /
        |-- nlp.py             <-- Sentiment and Theme extraction
        |-- ai_companion.py    <-- AWS Bedrock and Claude connection
        |-- database.py        <-- SQLite database storage and retrieval
        |-- summary.py         <-- Summary generation
        |-- themes.css         <-- UI elements that can't be done with Streamlit
        |-- app.py             <-- Main application UI using Streamlit

## Tech Stack
- Programming languages: Python
- NLP: Transformers sentiment pipeline
- AI Model: Claude Sonnet 3.5 v2 via AWS Bedrock
- Database and Storage: SQLite
- Frontend UI: Streamlit
- Frontend Styling: Streamlit + CSS

## Data Flow
    AI generates journal entry prompt
        |── user writes entry              
            |── sentiment and theme extracted
            |── AI generates thoughtful response to entry
            |── prompt and corresponding entry saved onto local database
        |── entry is used for trend visualization and weekly summary

## Future Enhancements
Some future enhancements if there was more time:
- Adding a feature that would let a user delete a journal entry, in case of a mess up
- Adding more nuanced themes to the nlp file so that the AI companion is able to analyze the user's entries better
- Adding better and more appealing UI components
        

