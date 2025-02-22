from django import forms
from .models import Incident, IncidentAttachment, IncidentLink, IncidentUpdate
from django.forms import inlineformset_factory

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'severity', 'start_date', 'end_date', 'details', 
                  'resolution_process', 'impact']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'details': forms.Textarea(attrs={'rows': 5}),
            'resolution_process': forms.Textarea(attrs={'rows': 5}),
            'impact': forms.Textarea(attrs={'rows': 5}),
        }


class IncidentAttachmentForm(forms.ModelForm):
    class Meta:
        model = IncidentAttachment
        fields = ['file', 'description']


class IncidentLinkForm(forms.ModelForm):
    class Meta:
        model = IncidentLink
        fields = ['url', 'title']


class IncidentUpdateForm(forms.ModelForm):
    class Meta:
        model = IncidentUpdate
        fields = ['update_text']
        widgets = {
            'update_text': forms.Textarea(attrs={'rows': 3}),
        }


# Create formsets for inline forms
AttachmentFormSet = inlineformset_factory(
    Incident, IncidentAttachment, form=IncidentAttachmentForm, extra=1, can_delete=True
)

LinkFormSet = inlineformset_factory(
    Incident, IncidentLink, form=IncidentLinkForm, extra=1, can_delete=True
)