from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('api/mood-chart-data/', views.mood_chart_data, name='mood_chart_data'),
    path('api/quick-mood/', views.quick_mood_entry, name='quick_mood_entry'),
]
