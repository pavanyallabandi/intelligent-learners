from django import forms
from .models import StudyGroup, Video

class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Master Python in 30 Days'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'What is this group about?'}),
        }

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'youtube_id', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Python Basics Part 1'}),
            'youtube_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Provide YouTube Video URL or ID'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display Order (e.g. 1)'}),
        }
        help_texts = {
            'youtube_id': "You can paste the full YouTube URL (e.g. https://www.youtube.com/watch?v=dQw4w9WgXcQ) or just the 11-character video ID."
        }

    def clean_youtube_id(self):
        url_or_id = self.cleaned_data.get('youtube_id')
        import re
        # Try to extract ID from various YouTube URL formats
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        match = re.search(youtube_regex, url_or_id)
        if match:
            return match.group(6)
        return url_or_id # Assuming it's already an ID
