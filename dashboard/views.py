from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
import json

from mood_tracking.models import MoodEntry
from mood_tracking.services import AIHelper


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent mood entries
        recent_moods = MoodEntry.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Get AI mood response from session if available
        ai_mood_response = self.request.session.pop('ai_mood_response', None)
        
        # Calculate mood statistics
        thirty_days_ago = datetime.now() - timedelta(days=30)
        mood_entries = MoodEntry.objects.filter(
            user=user, 
            created_at__gte=thirty_days_ago
        )
        
        mood_stats = {
            'total_entries': mood_entries.count(),
            'average_mood': 0,
            'mood_trend': 'stable'
        }
        
        if mood_entries.exists():
            mood_scores = list(mood_entries.values_list('mood_score', flat=True))
            mood_stats['average_mood'] = sum(mood_scores) / len(mood_scores)
            
            # Simple trend calculation
            if len(mood_scores) >= 2:
                recent_avg = sum(mood_scores[-5:]) / min(5, len(mood_scores))
                older_avg = sum(mood_scores[:-5]) / max(1, len(mood_scores) - 5)
                if recent_avg > older_avg + 0.2:
                    mood_stats['mood_trend'] = 'improving'
                elif recent_avg < older_avg - 0.2:
                    mood_stats['mood_trend'] = 'declining'
        
        context.update({
            'recent_moods': recent_moods,
            'mood_stats': mood_stats,
            'ai_mood_response': ai_mood_response,
        })
        
        return context


@login_required
def mood_chart_data(request):
    """API endpoint for mood chart data"""
    days = int(request.GET.get('days', 30))
    date_limit = datetime.now() - timedelta(days=days)
    
    mood_entries = MoodEntry.objects.filter(
        user=request.user,
        created_at__gte=date_limit
    ).order_by('created_at').values('mood_score', 'created_at')
    
    data = {
        'dates': [],
        'scores': [],
        'labels': []
    }
    
    mood_labels = {1: 'Very Low', 2: 'Low', 3: 'Neutral', 4: 'Good', 5: 'Excellent'}
    
    for entry in mood_entries:
        data['dates'].append(entry['created_at'].strftime('%Y-%m-%d'))
        data['scores'].append(entry['mood_score'])
        data['labels'].append(mood_labels.get(round(entry['mood_score']), 'Unknown'))
    
    return JsonResponse(data)


@login_required
def quick_mood_entry(request):
    """Quick mood entry via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mood_score = float(data.get('mood_score'))
            notes = data.get('notes', '')
            
            # Create mood entry
            mood_entry = MoodEntry.objects.create(
                user=request.user,
                mood_score=mood_score,
                notes=notes
            )
            
            # Get AI response
            ai_helper = AIHelper()
            ai_response = ai_helper.get_mood_response(mood_score, notes)
            
            return JsonResponse({
                'success': True,
                'message': 'Mood entry saved successfully!',
                'ai_response': ai_response
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
