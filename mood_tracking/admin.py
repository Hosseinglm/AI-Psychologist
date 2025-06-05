from django.contrib import admin
from .models import MoodEntry


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood_score', 'get_mood_display', 'created_at')
    list_filter = ('mood_score', 'created_at', 'user')
    search_fields = ('user__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'mood_score', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
