from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'เขียนรีวิวหนังเรื่องนี้...'
                
            
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select', # ใช้สไตล์ Dropdown ของ Bootstrap
            }),
        }