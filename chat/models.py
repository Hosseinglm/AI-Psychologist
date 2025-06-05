from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatMessage(models.Model):
    """
    Model to store chat messages between user and AI
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField(help_text="User's message")
    response = models.TextField(help_text="AI's response")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
    
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}..."
