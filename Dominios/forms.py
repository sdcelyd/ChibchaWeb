from django import forms

class VerificarURLForm(forms.Form):
    url = forms.URLField(label="URL a verificar", required=True, widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://ejemplo.com'
    }))

class AgregarDominioForm(forms.Form):
    dominio = forms.CharField(
        label="Dominio",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'ejemplo.com',
            'pattern': r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,})$'
        }),
        help_text="Ingresa solo el dominio (sin http:// o www)"
    )

    def clean_dominio(self):
        dominio = self.cleaned_data['dominio']
        # Limpiar el dominio de protocolos y www
        dominio = dominio.lower()
        if dominio.startswith('http://'):
            dominio = dominio[7:]
        if dominio.startswith('https://'):
            dominio = dominio[8:]
        if dominio.startswith('www.'):
            dominio = dominio[4:]
        
        # Validar formato básico de dominio
        import re
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,})$', dominio):
            raise forms.ValidationError("Formato de dominio inválido")
        
        return dominio
