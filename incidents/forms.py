from django import forms
from .models import Incident, IncidentLink, IncidentUpdate, Comment
from django.forms import inlineformset_factory
from django.utils import timezone
from .widgets import MultipleFileInput

"""
Django forms for the incident management system.
This module defines forms used for creating, editing and interacting with incidents
in the incident management system. It includes forms for the main incident data,
related links, updates, comments, and file uploads.
Forms:
    IncidentForm: Main form for incident creation and editing with file upload capability.
    IncidentLinkForm: Form for adding reference links to incidents.
    IncidentUpdateForm: Form for adding status updates to an existing incident.
    CommentForm: Form for adding comments to incidents.
FormSets:
    LinkFormSet: Inline formset for managing multiple links attached to an incident.
"""

class IncidentForm(forms.ModelForm):
    # Ajouter le champ files explicitement avec le widget MultipleFileInput
    files = forms.FileField(
        widget=MultipleFileInput(),
        required=False,
        label="Fichiers attachés"
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
        # Set initial values or customize form
        if not self.instance.pk:  # New incident
            self.fields['status'].initial = 'new'  # Changed from 'OPEN' to match STATUS_CHOICES
            self.fields['start_date'].initial = timezone.now()
        
        # Make certain fields not required in the form
        # as we will provide default values in the view
        self.fields['end_date'].required = False
        self.fields['resolution_process'].required = False
        self.fields['impact'].required = False
        self.fields['assigned_to'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Add any validation logic here
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if end_date and start_date and end_date < start_date:
            self.add_error('end_date', "La date de fin ne peut pas être antérieure à la date de début.")
        
        status = cleaned_data.get('status')
        if status == 'resolved' and not end_date:  # Changed from 'CLOSED' to match STATUS_CHOICES
            self.add_error('end_date', "Une date de fin est requise pour les incidents clôturés.")
        
        # Supprimer l'erreur sur le champ 'files' s'il y en a une
        if 'files' in self._errors:
            del self._errors['files']
            
        return cleaned_data


class IncidentLinkForm(forms.ModelForm):
    class Meta:
        model = IncidentLink
        fields = ['url', 'title']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control input input-bordered'}),
            'title': forms.TextInput(attrs={'class': 'form-control input input-bordered'}),
        }


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
LinkFormSet = inlineformset_factory(
    Incident, IncidentLink, form=IncidentLinkForm, extra=1, can_delete=True
)