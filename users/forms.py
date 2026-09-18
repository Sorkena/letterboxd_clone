from django import forms
from .models import CustomList, Genre

class CustomListForm(forms.ModelForm):
    class Meta:
        model = CustomList
        fields = ['title', 'description']
        labels = {
            'title': 'Liste Adı',
            'description': 'Açıklama (İsteğe bağlı)'
        }


class GenrePreferenceForm(forms.Form):
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )