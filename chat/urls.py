from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatView.as_view(), name='chat'),
    path('send/', views.send_message, name='send_message'),
    path('api/history/', views.chat_history_api, name='chat_history_api'),
]
