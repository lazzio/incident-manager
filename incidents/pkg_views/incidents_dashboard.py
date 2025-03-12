from django.shortcuts import render
from django.db.models import Count, F
from incidents.models import Incident
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request: object) -> object:
    """
    Renders the incident dashboard view.
    
    This view displays various statistics and information about incidents:
    - Total number of incidents
    - Number of open incidents
    - Number of in-progress incidents
    - Number of resolved incidents
    - Five most recent incidents
    - Breakdown of incidents by severity category with percentage calculations
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        HttpResponse: Rendered dashboard template with incident statistics context
    """
    total_incidents = Incident.objects.count()
    context = {
        'total_incidents': total_incidents,
        'open_incidents': Incident.objects.filter(status='new').count(),
        'in_progress_incidents': Incident.objects.filter(status='in_progress').count(),
        'resolved_incidents': Incident.objects.filter(status='resolved').count(),
        'recent_incidents': Incident.objects.order_by('-created_at')[:5],
        'categories': Incident.objects.values('severity').annotate(
            count=Count('id'),
            name=F('severity'),
            percentage=100.0 * Count('id') / total_incidents
        ).order_by('severity')
    }
    return render(request, 'incidents/incidents_dashboard.html', context)