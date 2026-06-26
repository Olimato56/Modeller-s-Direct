from django import forms
from .models import ModelKit

class ModelKitSubmission(forms.ModelForm):
    name = forms.CharField(
        required=True,
        error_messages={'required': 'A model name is required.'}
    )

    class Meta:
        model = ModelKit
        #everything to be filled out by the user
        fields = ['carmanufacturer', 'name', 'manufacturer', 'bodytype', 'roadrace', 'detail', 'modelyear', 'yearoftool', 'scale', 'coverimage']

        labels = {
            'manufacturer': 'Model Kit Manufacturer',
            'carmanufacturer': 'Manufacturer / Brand',
            'name': 'Model Name',
            'bodytype': 'Body Type',
            'roadrace': 'Classification',
            'detail': 'Level of Detail',
            'yearoftool': 'Tooling Year',
            'scale': 'Scale',
            'modelyear': 'Model Year',
            'coverimage': 'Box Art'
        }

    def clean_name(self):
        name_value = self.cleaned_data.get('name', '').strip()
        if not name_value:
            raise forms.ValidationError("Your model name cannot be completely blank.")
        name_exists = ModelKit.objects.filter(name__iexact=name_value)
        if self.instance and self.instance.pk:
            name_exists = name_exists.exclude(pk=self.instance.pk)
        if name_exists.exists():
            raise forms.ValidationError(f"A model kit named '{name_value}' already exists in the database.")            
        return name_value