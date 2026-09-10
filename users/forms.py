from django import forms
from .models import CustomList

class CustomListForm(forms.ModelForm):
    class Meta:
        model = CustomList
        fields = ['title', 'description']
        labels = {
            'title': 'Liste Adı',
            'description': 'Açıklama (İsteğe bağlı)'
        }