"""
Django forms for lessonplanner endpoints.

These forms provide validation for API requests using Django's native form system.
CSRF protection is automatically handled by Django middleware.
"""

from django import forms


class FillWorkPlanForm(forms.Form):
    """
    Form for POST /api/fill-work-plan endpoint.

    Validates teacher's activity description and optional theme.
    """
    activity = forms.CharField(
        max_length=500,
        min_length=1,
        required=True,
        error_messages={
            'required': "Pole 'activity' jest wymagane",
            'min_length': "Pole 'activity' nie może być puste",
            'max_length': "Pole 'activity' jest za długie (max 500 znaków)",
        },
        widget=forms.TextInput(attrs={'placeholder': 'Opis aktywności'})
    )

    theme = forms.CharField(
        max_length=200,
        required=False,
        error_messages={
            'max_length': "Pole 'theme' jest za długie (max 200 znaków)",
        },
        widget=forms.TextInput(attrs={'placeholder': 'Temat tygodnia (opcjonalnie)'})
    )

    def clean_activity(self):
        """Strip whitespace and ensure activity is not empty."""
        activity = self.cleaned_data.get('activity', '').strip()
        if not activity:
            raise forms.ValidationError("Pole 'activity' nie może być puste")
        return activity

    def clean_theme(self):
        """Strip whitespace from theme if provided."""
        theme = self.cleaned_data.get('theme', '')
        if theme:
            return theme.strip()
        return theme
