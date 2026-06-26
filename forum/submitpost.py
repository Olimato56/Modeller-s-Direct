from django import forms
from .models import Post

class PostSubmission(forms.ModelForm):
    posttitle = forms.CharField(
        label='Post Title',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        error_messages={'required': 'A post title is required.'}
    )

    class Meta:
        model = Post
        fields = ['posttitle', 'posttext']
        labels = {
            'posttext': 'Post Content',
        }

    def clean_posttitle(self):
            title_value = self.cleaned_data.get('posttitle', '').strip()
            if not title_value:
                raise forms.ValidationError("Your post title cannot be completely blank.")
            title_exists = Post.objects.filter(posttitle__iexact=title_value)
            if self.instance and self.instance.pk:
                title_exists = title_exists.exclude(pk=self.instance.pk)
            if title_exists.exists():
                raise forms.ValidationError(f"A forum post titled '{title_value}' already exists.")  
            return title_value