from django.shortcuts import render
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from incidents.models import Incident
import datetime
from django.http import JsonResponse
from openpyxl import Workbook
from django.http import HttpResponse


@login_required
def yearly_report(request: object) -> HttpResponse:
    """
    Generate a yearly report of incidents with various analytics.
    This view produces a comprehensive report of incidents for a specified year,
    including statistics on incident counts by severity and month, resolution times,
    and comparisons with previous years.
    Parameters:
    ----------
    request : HttpRequest
        The HTTP request object. Can contain a 'year' query parameter to specify
        which year to generate the report for. If not provided, defaults to the current year.
    Returns:
    -------
    HttpResponse
        Renders the 'incidents/incidents_yearly_report.html' template with the following context:
        - year: int - The year for which the report is generated
        - total_incidents: int - Total number of incidents in the selected year
        - severity_counts: QuerySet - Incidents grouped by severity with counts
        - monthly_counts: QuerySet - Incidents grouped by month with counts
        - avg_resolution_time: float - Average resolution time in hours
        - longest_incidents: QuerySet - Top 5 incidents with the longest duration
        - duration_by_severity: QuerySet - Average resolution time by severity level
        - prev_year_data: dict or None - Previous year's comparison data if available
        - yearly_trend: list - Count of incidents for each year in the database
        - available_years: list - All years that have incidents recorded
    Notes:
    -----
    Resolution times are calculated in hours. The function handles the case where
    incidents may have no duration information by excluding them from calculations.
    """
    year = request.GET.get('year', datetime.datetime.now().year)
    year = int(year)
    
    # Get incidents for the selected year
    incidents = Incident.objects.filter(start_date__year=year)
    
    # Count incidents by severity
    severity_counts = incidents.values('severity').annotate(count=Count('id')).order_by('severity')
    
    # Count incidents by month
    monthly_counts = incidents.annotate(month=TruncMonth('start_date')).values('month').annotate(count=Count('id')).order_by('month')
    
    # Calculate average resolution time
    resolution_times = []
    for incident in incidents:
        if incident.duration:
            resolution_times.append(incident.duration.total_seconds() / 3600)  # Convert to hours
    
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    # Get average resolution time by severity
    duration_by_severity = incidents.exclude(duration=None).values('severity').annotate(
        avg_duration=Avg(
            ExpressionWrapper(F('duration'), output_field=fields.DurationField()) / 3600000000  # Convert microseconds to hours
        )
    ).order_by('severity')
    
    # Get top 5 longest incidents
    longest_incidents = incidents.exclude(duration=None).order_by('-duration')[:5]
    
    # Get previous year's data for comparison
    prev_year_data = None
    prev_year_incidents = Incident.objects.filter(start_date__year=year-1)
    if prev_year_incidents.exists():
        prev_year_resolution_times = []
        for incident in prev_year_incidents:
            if incident.duration:
                prev_year_resolution_times.append(incident.duration.total_seconds() / 3600)
        
        prev_year_avg_resolution_time = sum(prev_year_resolution_times) / len(prev_year_resolution_times) if prev_year_resolution_times else 0
        
        prev_year_data = {
            'total_incidents': prev_year_incidents.count(),
            'avg_resolution_time': prev_year_avg_resolution_time
        }
    
    # Get yearly trend data
    yearly_trend = []
    available_years = [date.year for date in Incident.objects.dates('start_date', 'year')]
    for trend_year in available_years:
        yearly_trend.append({
            'year': trend_year,
            'count': Incident.objects.filter(start_date__year=trend_year).count()
        })
    
    context = {
        'year': year,
        'total_incidents': incidents.count(),
        'severity_counts': severity_counts,
        'monthly_counts': monthly_counts,
        'avg_resolution_time': avg_resolution_time,
        'longest_incidents': longest_incidents,
        'duration_by_severity': duration_by_severity,
        'prev_year_data': prev_year_data,
        'yearly_trend': yearly_trend,
        
        # Get all years that have incidents
        'available_years': available_years,
    }
    
    return render(request, 'incidents/incidents_yearly_report.html', context)


@login_required
def incident_chart_data(request: object) -> JsonResponse:
    """
    Generate chart data for incidents based on the requested year.
    This function processes incident data to create visualizations including:
    - Monthly incident count
    - Incident count by severity
    - Average incident duration by severity (in hours)
    - Yearly incident trends
    Parameters:
    -----------
    request : object
        HTTP request object that may contain a 'year' GET parameter.
        If not provided, defaults to the current year.
    Returns:
    --------
    JsonResponse
        A JSON response containing the following data:
        - months: List of month names (abbreviated)
        - counts: Monthly incident counts
        - severity_labels: List of severity levels
        - severity_counts: Incident counts by severity
        - duration_by_severity: List of dictionaries with severity and average duration in hours
        - yearly_trend: List of dictionaries with year and incident count
    Notes:
    ------
    Duration values are converted from Django timedelta to hours and rounded to 2 decimal places.
    Only incidents with non-null duration values are included in duration calculations.
    """
    year = request.GET.get('year', datetime.datetime.now().year)
    incidents = Incident.objects.filter(start_date__year=year)
    
    # Monthly data
    monthly_data = list(incidents.annotate(
        month=TruncMonth('start_date')
    ).values('month').annotate(count=Count('id')).order_by('month'))
    
    # Convert to chart-friendly format
    months = []
    counts = []
    
    for item in monthly_data:
        months.append(item['month'].strftime('%b'))
        counts.append(item['count'])
    
    # Severity data
    severity_data = list(incidents.values('severity').annotate(count=Count('id')))
    severity_labels = [item['severity'] for item in severity_data]
    severity_counts = [item['count'] for item in severity_data]
    
    # Duration by severity - Correction de l'erreur ici
    duration_data = []
    for severity in incidents.values_list('severity', flat=True).distinct():
        avg_duration = incidents.filter(
            severity=severity, 
            duration__isnull=False
        ).aggregate(
            avg=Avg('duration')
        )['avg']
        
        if avg_duration:
            # Convertir la durée moyenne en heures (en secondes divisées par 3600)
            hours = avg_duration.total_seconds() / 3600
            duration_data.append({
                'severity': severity,
                'avg_duration': round(hours, 2)  # Arrondir à 2 décimales
            })
    
    # Yearly trend data
    yearly_trend = []
    available_years = [date.year for date in Incident.objects.dates('start_date', 'year')]
    for trend_year in available_years:
        yearly_trend.append({
            'year': trend_year,
            'count': Incident.objects.filter(start_date__year=trend_year).count()
        })
    
    data = {
        'months': months,
        'counts': counts,
        'severity_labels': severity_labels,
        'severity_counts': severity_counts,
        'duration_by_severity': duration_data,
        'yearly_trend': yearly_trend
    }
    
    return JsonResponse(data)


@login_required
def export_yearly_report(request: object, year: int) -> HttpResponse:
    """
    Generate and export an Excel report of incidents for a specific year.
    This function creates an Excel workbook containing monthly statistics about incidents
    for the specified year, including the count of incidents per month.
    Args:
        request: The HTTP request object.
        year: The year for which to generate the report.
    Returns:
        HttpResponse: A response containing the Excel file for download with proper content type
                     and disposition headers set.
    Note:
        The exported Excel file will be named 'rapport_incidents_{year}.xlsx'.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = f"Rapport {year}"
    
    # Headers
    headers = ['Month', 'Number of incidents', 'Resolution average time']
    ws.append(headers)
    
    # Monthly data
    incidents = Incident.objects.filter(start_date__year=year)
    monthly_data = (incidents.annotate(month=TruncMonth('start_date'))
                   .values('month')
                   .annotate(count=Count('id'))
                   .order_by('month'))
    
    for data in monthly_data:
        ws.append([
            data['month'].strftime('%B %Y'),
            data['count'],
        ])
    
    # Prepare response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=rapport_incidents_{year}.xlsx'
    
    wb.save(response)
    return response