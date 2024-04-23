from django import forms

from .models import MarketingPref

class MarketingPrefForm(forms.ModelForm):
    subscribed = forms.BooleanField(label="Recieve news and updates?", required=False)
    class Meta:
        model = MarketingPref
        fields = [ 'subscribed']