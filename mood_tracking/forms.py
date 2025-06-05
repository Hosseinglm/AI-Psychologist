from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div, HTML
from .models import MoodEntry


class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood_score', 'notes']
        widgets = {
            'mood_score': forms.NumberInput(attrs={
                'type': 'range',
                'min': '1',
                'max': '5',
                'step': '0.1',
                'class': 'form-range',
                'id': 'mood-slider'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'How are you feeling today? (optional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="mood-slider-container mb-4">'),
            HTML('<label for="mood-slider" class="form-label">How are you feeling?</label>'),
            HTML('<div class="d-flex justify-content-between mb-2">'),
            HTML('<small class="text-muted">Very Low</small>'),
            HTML('<small class="text-muted">Excellent</small>'),
            HTML('</div>'),
            Field('mood_score'),
            HTML('<div class="text-center mt-2">'),
            HTML('<span id="mood-value" class="badge bg-primary fs-6">3.0</span>'),
            HTML('</div>'),
            HTML('</div>'),
            Field('notes'),
            Submit('submit', 'Save Mood Entry', css_class='btn btn-primary w-100 mt-3')
        )
