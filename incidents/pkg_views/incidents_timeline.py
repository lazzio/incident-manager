from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
from incidents.models import Incident


class IncidentTimelineView(LoginRequiredMixin, ListView):
    """
    View for displaying incidents in a timeline format by year.
    This view shows incidents ordered by start date for a specific year
    (defaults to the current year if not specified). The view requires
    user authentication.
    Attributes:
        model: The Incident model to query data from.
        template_name: The HTML template used to render the view.
        context_object_name: The variable name used in the template for the incidents queryset.
    Methods:
        get_queryset: Filters incidents by the selected year.
        get_context_data: Adds selected year and available years to the template context.
    """
    model = Incident
    template_name = 'incidents/incidents_timeline.html'
    context_object_name = 'incidents'

    def get_queryset(self):
        year = self.request.GET.get('year', datetime.datetime.now().year)
        return Incident.objects.filter(start_date__year=year).order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_year'] = int(self.request.GET.get('year', datetime.datetime.now().year))
        
        # Get all years that have incidents
        years = Incident.objects.dates('start_date', 'year')
        context['available_years'] = [date.year for date in years]
        
        return context