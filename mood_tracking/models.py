from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class MoodEntry(models.Model):
    """
    Model to store user mood entries
    """
    MOOD_CHOICES = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Neutral'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_entries')
    mood_score = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text="Mood score from 1 (very low) to 5 (excellent)"
    )
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about your mood")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mood Entry'
        verbose_name_plural = 'Mood Entries'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_mood_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_mood_display(self):
        """Return human-readable mood level"""
        mood_map = {
            1: 'Very Low',
            2: 'Low', 
            3: 'Neutral',
            4: 'Good',
            5: 'Excellent'
        }
        # Handle float values by rounding to nearest integer
        rounded_score = round(self.mood_score)
        return mood_map.get(rounded_score, f'Score: {self.mood_score}')
