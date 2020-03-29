from django import forms
from .models import *

class PictureForm(forms.ModelForm):

    class Meta:
        model = Picture
        fields = ['name', 'picture_image']

class LocationForm(forms.ModelForm):
    locations = forms.ModelMultipleChoiceField(queryset=Location.objects.all())
