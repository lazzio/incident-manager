
from incidents.models import Incident, Severity
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class IncidentListView(LoginRequiredMixin, ListView):
    """
    View for displaying a list of incidents with filtering and pagination.
    This view requires authentication and provides a paginated list of incidents 
    that can be filtered by search terms, status, and severity. Results are ordered
    by creation date (newest first).
    Attributes:
        model (Model): The Incident model.
        template_name (str): Path to the template for displaying the incidents list.
        context_object_name (str): Name of the variable to use in the template.
        paginate_by (int): Number of incidents per page.
    URL Parameters:
        search (str, optional): Filters incidents by title containing this text.
        status (str, optional): Filters incidents by their status.
        severity (str, optional): Filters incidents by their severity level.
    """
    model = Incident
    template_name = 'incidents/incidents_list.html'
    context_object_name = 'incidents'
    paginate_by = 10

    def get_queryset(self):
        queryset = Incident.objects.all()
        # Get filters from the URL
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        severity = self.request.GET.get('severity')

        # Apply filters
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        if status:
            queryset = queryset.filter(status=status)
            
        if severity:
            queryset = queryset.filter(severity=severity)

        # Sort by descending creation date
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Incident.STATUS_CHOICES
        context['severity_choices'] = Severity.choices
        return context