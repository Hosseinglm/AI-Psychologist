from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'message', 'response')
    readonly_fields = ('created_at',)
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
