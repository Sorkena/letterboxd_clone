from django import forms
from .models import Review, MovieRating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        labels = {
            'rating': 'Puanınız (1-10)',
            'content': 'İncelemeniz (İsteğe bağlı)'
        }
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 10, 'style': 'padding: 8px; width: 80px; background: #14171c; color: #fff; border: 1px solid #2c3643; border-radius: 4px;'}),
            'content': forms.Textarea(attrs={'rows': 3, 'style': 'width: 100%; padding: 10px; margin-top:5px; background: #14171c; color: #fff; border: 1px solid #2c3643; border-radius: 4px; box-sizing: border-box;'}),
        }
class RatingForm(forms.ModelForm):
    class Meta:
        model = MovieRating
        fields = ['rating']
        labels = {
            'rating': 'Güncel puanınız (1-10)'
        }

        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1,'max': 10,'style': 'padding: 8px; width: 80px; background: #14171c; color: #fff; border: 1px solid #2c3643; border-radius: 4px;'}),
        }