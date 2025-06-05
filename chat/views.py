from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import ChatMessage
from mood_tracking.services import AIHelper


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent chat history
        chat_history = ChatMessage.objects.filter(user=self.request.user)[:20]
        context['chat_history'] = reversed(chat_history)
        
        return context


@login_required
@csrf_exempt
def send_message(request):
    """Handle sending messages to AI via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({
                    'success': False,
                    'error': 'Message cannot be empty'
                })
            
            # Get recent chat history for context
            recent_chats = ChatMessage.objects.filter(user=request.user)[:5]
            chat_history = list(reversed(recent_chats))
            
            # Get AI response
            ai_helper = AIHelper()
            response = ai_helper.get_chat_response(message, chat_history)
            
            # Save chat message
            chat_message = ChatMessage.objects.create(
                user=request.user,
                message=message,
                response=response
            )
            
            return JsonResponse({
                'success': True,
                'response': response,
                'timestamp': chat_message.created_at.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def chat_history_api(request):
    """API endpoint to get chat history"""
    limit = int(request.GET.get('limit', 20))
    
    chat_messages = ChatMessage.objects.filter(user=request.user)[:limit]
    
    data = []
    for chat in reversed(chat_messages):
        data.append({
            'id': chat.id,
            'message': chat.message,
            'response': chat.response,
            'created_at': chat.created_at.isoformat()
        })
    
    return JsonResponse({'chat_history': data})
