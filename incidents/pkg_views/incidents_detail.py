from incidents.models import Incident
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from incidents.forms import IncidentUpdateForm, CommentForm


class IncidentDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for displaying a single Incident.
    This view inherits from Django's DetailView and LoginRequiredMixin to ensure
    only authenticated users can view incident details.
    The page displays incident information along with its related updates, comments,
    and uploaded files. It also provides forms for adding new updates and comments.
    Attributes:
        model: The Incident model to retrieve objects from
        template_name: The template used to render the view
        context_object_name: The name used for the incident object in the template context
    Methods:
        get_context_data: Extends the context with related data (updates, comments, files)
                         and forms for user interaction
    """
    model = Incident
    template_name = 'incidents/incidents_detail.html'
    context_object_name = 'incident'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = self.object.updates.all()
        context['update_form'] = IncidentUpdateForm()
        context['comments'] = self.object.comments.all()
        context['comment_form'] = CommentForm()
        context['incident_files'] = self.object.files.all().order_by('-uploaded_at')
        return context