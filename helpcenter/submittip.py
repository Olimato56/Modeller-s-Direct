from django import forms
from .models import UserHelp

class TipSubmission(forms.ModelForm):
    helptitle = forms.CharField(
        label='Tip Title',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        error_messages={'required': 'A tip title is required.'}
    )

    class Meta:
        model = UserHelp
        fields = ['helptitle', 'helptext']
        labels = {
            'helptext': 'Tip Content',
        }

    def clean_helptitle(self):
            title_value = self.cleaned_data.get('helptitle', '').strip()
            if not title_value:
                raise forms.ValidationError("Your tip title cannot be completely blank.")
            title_exists = UserHelp.objects.filter(helptitle__iexact=title_value)
            if self.instance and self.instance.pk:
                title_exists = title_exists.exclude(pk=self.instance.pk)
            if title_exists.exists():
                raise forms.ValidationError(f"A tipt titled '{title_value}' already exists.")  
            return title_value