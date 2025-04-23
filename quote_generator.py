import random
from datetime import datetime
import json
from ai_helper import AIHelper

class QuoteGenerator:
    def __init__(self, ai_helper: AIHelper):
        self.ai_helper = ai_helper

    def generate_daily_quote(self, mood_history=None, user_id=None):
        try:
            # Get current date for consistency
            current_date = datetime.now().strftime("%Y-%m-%d")

            # Create a context-aware prompt based on mood history
            context = self._create_context(mood_history) if mood_history else ""

            response = self.ai_helper.client.chat.completions.create(
                model="gpt-4o",  # Using the latest model
                messages=[
                    {
                        "role": "system",
                        "content": """You are a mental health quote generator specializing in 
                        creating uplifting, meaningful, and personalized quotes. Generate a daily
                        inspirational quote that resonates with the user's emotional state.
                        Respond with JSON in this format:
                        {
                            'quote': string,
                            'author': string,
                            'reflection': string,
                            'theme': string,
                            'mood_boost_tips': list[string]
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"Generate an inspirational quote for today ({current_date}). {context}"
                    }
                ],
                response_format={"type": "json_object"}
            )

            # Ensure we're returning a parsed JSON object
            return json.loads(response.choices[0].message.content)

        except Exception as e:
            # Fallback quotes for when API fails
            fallback_quotes = [
                {
                    "quote": "Every moment is a fresh beginning.",
                    "author": "T.S. Eliot",
                    "reflection": "Each day brings new opportunities for growth and healing.",
                    "theme": "New Beginnings",
                    "mood_boost_tips": ["Take a deep breath", "Start with small steps"]
                },
                {
                    "quote": "You are stronger than you know.",
                    "author": "Unknown",
                    "reflection": "Your resilience shines even in difficult moments.",
                    "theme": "Inner Strength",
                    "mood_boost_tips": ["Celebrate small wins", "Practice self-compassion"]
                }
            ]
            return random.choice(fallback_quotes)

    def _create_context(self, mood_history):
        """Create context from mood history for more personalized quotes"""
        if not mood_history:
            return ""

        # Calculate average mood from recent history
        recent_moods = [entry['mood_score'] for entry in mood_history[-7:]]  # Last 7 entries
        avg_mood = sum(recent_moods) / len(recent_moods) if recent_moods else 3

        # Create appropriate context based on mood trend
        if avg_mood <= 2:
            return "The user has been experiencing lower moods recently. Focus on hope and resilience."
        elif avg_mood <= 3:
            return "The user has been having moderate moods. Focus on growth and potential."
        else:
            return "The user has been experiencing positive moods. Focus on gratitude and maintaining wellbeing."