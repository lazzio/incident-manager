from django import forms
from .models import Incident, IncidentLink, IncidentUpdate, Comment, IncidentFile
from django.forms import inlineformset_factory
from django.utils import timezone

class IncidentForm(forms.ModelForm):
    files = forms.FileField(
        required=False,
        help_text='Vous pouvez sélectionner plusieurs fichiers.'
    )
    
    class Meta:
        model = Incident
        fields = [
            'title', 'category', 'status', 'severity',
            'start_date', 'end_date', 'details', 'resolution_process', 'impact', 'assigned_to'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'details': forms.Textarea(attrs={'rows': 5}),
            'resolution_process': forms.Textarea(attrs={'rows': 3}),
            'impact': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre la date de début obligatoire avec valeur par défaut
        if not self.initial.get('start_date'):
            self.initial['start_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
        
        # Rendre certains champs non obligatoires dans le formulaire
        # car nous fournirons des valeurs par défaut dans la vue
        self.fields['resolution_process'].required = False
        self.fields['impact'].required = False


# class IncidentAttachmentForm(forms.ModelForm):
#     class Meta:
#         model = IncidentAttachment
#         fields = ['file', 'description']


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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


# Create formsets for inline forms
# AttachmentFormSet = inlineformset_factory(
#     Incident, IncidentAttachment, form=IncidentAttachmentForm, extra=1, can_delete=True
# )

LinkFormSet = inlineformset_factory(
    Incident, IncidentLink, form=IncidentLinkForm, extra=1, can_delete=True
)