from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from incidents.models import Incident


class IncidentDeleteView(LoginRequiredMixin, DeleteView):
    """
    A view for deleting incidents.

    This view inherits from Django's DeleteView and LoginRequiredMixin to ensure that
    only authenticated users can delete incidents. It provides a confirmation page
    before actually deleting an incident.

    Attributes:
        model (Model): The Incident model that this view operates on.
        template_name (str): Path to the template used for the confirmation page.
        success_url (str): URL to redirect to after successful deletion, in this case
                          the incident list page.
    """
    model = Incident
    template_name = 'incidents/incidents_confirm_delete.html'
    success_url = reverse_lazy('incident_list')