from django import forms

class VerificarURLForm(forms.Form):
    url = forms.URLField(label="URL a verificar", required=True, widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://ejemplo.com'
    }))
