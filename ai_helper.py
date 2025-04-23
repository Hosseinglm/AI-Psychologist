import os
import json
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

class AIHelper:
    def __init__(self):
        #self.client = OpenAI(api_key=os.environ.get("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"))
        self.client = OpenAI(api_key="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")

    def get_mood_response(self, mood_score, notes):
        try:
            # First, analyze the text sentiment independently
            text_sentiment = self._analyze_text_sentiment(notes) if notes else None

            # Combine slider score with text sentiment
            effective_mood = self._combine_mood_scores(mood_score, text_sentiment)

            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a compassionate mental health assistant. 
                        Analyze both the numerical mood score and the user's notes to provide 
                        empathetic feedback. Pay special attention to the content of their notes. 
                        Respond with JSON in this format: 
                        {
                            'message': string, 
                            'suggestions': list[string],
                            'analyzed_mood': {
                                'score': number,
                                'factors': list[string]
                            }
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"Mood score: {mood_score}\nNotes: {notes}\nAnalyzed text sentiment: {text_sentiment}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "message": "I'm here to listen and support you.",
                "suggestions": ["Take a deep breath", "Consider talking to a friend"],
                "analyzed_mood": {
                    "score": mood_score,
                    "factors": ["Based on reported mood score"]
                }
            }

    def _analyze_text_sentiment(self, text):
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the emotional content of the text and provide a mood score between 1-5, 
                        where 1 is very negative and 5 is very positive. Respond with JSON in this format:
                        {
                            'score': number,
                            'key_emotions': list[string],
                            'confidence': number
                        }"""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return None

    def _combine_mood_scores(self, slider_score, text_sentiment):
        if not text_sentiment:
            return slider_score

        text_score = text_sentiment.get('score', slider_score)
        confidence = text_sentiment.get('confidence', 0.5)

        # Weighted average based on confidence of text analysis
        return (slider_score * (1 - confidence) + text_score * confidence)

    def get_chat_response(self, message, chat_history=None):
        try:
            context = []
            if chat_history:
                for entry in chat_history[-3:]:  # Use last 3 messages for context
                    context.extend([
                        {"role": "user", "content": entry["message"]},
                        {"role": "assistant", "content": entry["response"]}
                    ])

            context.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a compassionate mental health assistant.
                        Provide empathetic, supportive responses while maintaining
                        appropriate boundaries. Never provide medical advice or diagnoses.
                        Focus on active listening and emotional support."""
                    }
                ] + context,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return "I'm here to listen and support you. Would you like to tell me more?"