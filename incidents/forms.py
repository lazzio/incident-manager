from django import forms
from .models import Incident, IncidentLink, IncidentUpdate, Comment
from django.forms import inlineformset_factory
from django.utils import timezone
from .widgets import MultipleFileInput
from django.utils.translation import gettext as _

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
    # Add the files field explicitly with the MultipleFileInput widget
    files = forms.FileField(
        widget=MultipleFileInput(),
        required=False,
        label=_("attached files"),
        help_text=_("Max. 10 MB")
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
            # 'details' n'a pas besoin de widget personnalisé car QuillField fournit son propre widget
            #'resolution_process': forms.Textarea(attrs={'rows': 3}),
            #'impact': forms.Textarea(attrs={'rows': 3}),
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
        
        # Ajouter une classe CSS aux champs QuillField
        if 'resolution_process' in self.fields:
            self.fields['resolution_process'].widget.attrs.update({
                'class': 'border border-gray-300 rounded'
            })
        if 'impact' in self.fields:
            self.fields['impact'].widget.attrs.update({
                'class': 'border border-gray-300 rounded'
            })
        if 'details' in self.fields:
            self.fields['details'].widget.attrs.update({
                'class': 'border border-gray-300 rounded'
            })
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Add any validation logic here
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if end_date and start_date and end_date < start_date:
            self.add_error('end_date', _("end date can't be prior to start date"))
        
        status = cleaned_data.get('status')
        if status == 'resolved' and not end_date:  # Changed from 'CLOSED' to match STATUS_CHOICES
            self.add_error('end_date', _("end date is required for resolved incidents"))
        
        # Delete the error on the 'files' field if there is one
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