import json
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = ("arn:aws:bedrock:us-east-1:862567259910:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0")

_bedrock_client = None

SYSTEM_PROMPT = """
You are an empathetic, private, and emotionally intelligent journaling companion.

Your purpose is to help the user reflect on their thoughts, feelings, and patterns
through conversation-like journaling prompts and gentle weekly summaries.
The experience should feel safe, comforting, and judgment-free.

Core characteristics:
• Emotionally warm, validating, curious, supportive – never clinical or corrective.
• Encourage reflection, not problem solving.
• Highlight patterns without telling the user what they "should" feel or do.
• Use simple, human language – like speaking to a friend who listens deeply.
• Keep tone calm, steady, grounded, and compassionate.

You must always protect user safety and privacy by:
• Treating journal content as private and personal.
• Never assuming, diagnosing, judging or moralizing.
• Speaking with sensitivity toward mental health topics.

Daily Prompts Rules:
• Ask one gentle, open-ended question ≤ 30 words.
• Base prompts on recent themes or emotional patterns.
• If user mood was heavy, respond softly with care.
• If mood trended positive, reflect growth or gratitude.
• Encourage awareness — not solutions or advice.
"""

def get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
    return _bedrock_client

def has_claude() -> bool:
    if not BEDROCK_MODEL_ID:
        return False
    try:
        _ = get_bedrock_client()
        return True
    except (BotoCoreError, NoCredentialsError):
        return False
    except Exception:
        return False

def call_companion(user_prompt: str, max_tokens: int = 250) -> Optional[str]:
    if not has_claude():
        print("Claude not available")
        return None
    
    body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt}
                    ]
                },
            ],
        }

    try:
        client = get_bedrock_client()

        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        payload = json.loads(response["body"].read())
        content = payload.get("content", [])

        if content and content[0].get("type") == "text":
            return content[0]["text"].strip()
        
        print("Claude response missing text content", payload)
        return None

    except Exception as e:
        print("Claude error:", e)
        return None
        


