from .models import CourseCategoryDetails
from django.forms import ModelForm
from django.forms.widgets import TextInput

class CategoryForm(ModelForm):
    class Meta:
        model = CourseCategoryDetails
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }