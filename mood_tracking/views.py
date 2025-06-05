from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import MoodEntry
from .forms import MoodEntryForm
from .services import AIHelper


class MoodEntryCreateView(LoginRequiredMixin, CreateView):
    model = MoodEntry
    form_class = MoodEntryForm
    template_name = 'mood_tracking/add_mood.html'
    success_url = reverse_lazy('dashboard:home')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Get AI response for the mood entry
        ai_helper = AIHelper()
        ai_response = ai_helper.get_mood_response(
            form.instance.mood_score,
            form.instance.notes
        )
        
        # Store AI response in session for display on dashboard
        self.request.session['ai_mood_response'] = ai_response
        
        messages.success(self.request, 'Mood entry saved successfully!')
        return response


class MoodHistoryView(LoginRequiredMixin, ListView):
    model = MoodEntry
    template_name = 'mood_tracking/history.html'
    context_object_name = 'mood_entries'
    paginate_by = 20
    
    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user)


@login_required
def mood_data_api(request):
    """API endpoint to get mood data for visualizations"""
    days = int(request.GET.get('days', 30))
    date_limit = datetime.now() - timedelta(days=days)
    
    mood_entries = MoodEntry.objects.filter(
        user=request.user,
        created_at__gte=date_limit
    ).values('mood_score', 'created_at', 'notes')
    
    data = []
    for entry in mood_entries:
        data.append({
            'mood_score': entry['mood_score'],
            'created_at': entry['created_at'].isoformat(),
            'notes': entry['notes'] or ''
        })
    
    return JsonResponse({'mood_history': data})
