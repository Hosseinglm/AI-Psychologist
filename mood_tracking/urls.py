from django.urls import path
from . import views

app_name = 'mood_tracking'

urlpatterns = [
    path('add/', views.MoodEntryCreateView.as_view(), name='add_mood'),
    path('history/', views.MoodHistoryView.as_view(), name='history'),
    path('api/data/', views.mood_data_api, name='mood_data_api'),
]
