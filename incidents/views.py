from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, F, ExpressionWrapper, fields

from .models import Incident, Severity
from .forms import (
    IncidentForm, IncidentUpdateForm, AttachmentFormSet, LinkFormSet
)

import datetime

class IncidentListView(LoginRequiredMixin, ListView):
    model = Incident
    template_name = 'incidents/incident_list.html'
    context_object_name = 'incidents'
    paginate_by = 10

    def get_queryset(self):
        queryset = Incident.objects.all()
        # Récupération des paramètres de filtrage
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        severity = self.request.GET.get('severity')

        # Application des filtres
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        if status:
            queryset = queryset.filter(status=status)
            
        if severity:
            queryset = queryset.filter(severity=severity)

        # Tri par date de création décroissante
        print(queryset)
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Incident.STATUS_CHOICES
        context['severity_choices'] = Severity.choices
        return context


class IncidentDetailView(LoginRequiredMixin, DetailView):
    model = Incident
    template_name = 'incidents/incident_detail.html'
    context_object_name = 'incident'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = self.object.updates.all()
        context['update_form'] = IncidentUpdateForm()
        return context


@login_required
def create_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        attachment_formset = AttachmentFormSet(request.POST, request.FILES, prefix='attachments')
        link_formset = LinkFormSet(request.POST, prefix='links')
        
        if form.is_valid() and attachment_formset.is_valid() and link_formset.is_valid():
            incident = form.save(commit=False)
            incident.created_by = request.user
            incident.save()
            
            attachment_formset.instance = incident
            attachment_formset.save()
            
            link_formset.instance = incident
            link_formset.save()
            
            return redirect('incident_detail', pk=incident.pk)
    else:
        form = IncidentForm()
        attachment_formset = AttachmentFormSet(prefix='attachments')
        link_formset = LinkFormSet(prefix='links')
    
    return render(request, 'incidents/incident_form.html', {
        'form': form,
        'attachment_formset': attachment_formset,
        'link_formset': link_formset,
        'status_choices': Incident.STATUS_CHOICES,
        'severity_choices': Severity.choices
    })


@login_required
def update_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        attachment_formset = AttachmentFormSet(request.POST, request.FILES, instance=incident, prefix='attachments')
        link_formset = LinkFormSet(request.POST, instance=incident, prefix='links')
        
        if form.is_valid() and attachment_formset.is_valid() and link_formset.is_valid():
            form.save()
            attachment_formset.save()
            link_formset.save()
            
            return redirect('incident_detail', pk=incident.pk)
    else:
        form = IncidentForm(instance=incident)
        attachment_formset = AttachmentFormSet(instance=incident, prefix='attachments')
        link_formset = LinkFormSet(instance=incident, prefix='links')
    
    return render(request, 'incidents/incident_form.html', {
        'form': form,
        'attachment_formset': attachment_formset,
        'link_formset': link_formset,
        'incident': incident,
    })


@login_required
def add_incident_update(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    
    if request.method == 'POST':
        form = IncidentUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.incident = incident
            update.updated_by = request.user
            update.save()
    
    return redirect('incident_detail', pk=pk)


class IncidentDeleteView(LoginRequiredMixin, DeleteView):
    model = Incident
    template_name = 'incidents/incident_confirm_delete.html'
    success_url = reverse_lazy('incident_list')


class IncidentTimelineView(LoginRequiredMixin, ListView):
    model = Incident
    template_name = 'incidents/timeline.html'
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


@login_required
def yearly_report(request):
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
    
    return render(request, 'incidents/yearly_report.html', context)

@login_required
def incident_chart_data(request):
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
    
    # Duration by severity
    duration_by_severity = list(incidents.exclude(duration=None).values('severity').annotate(
        avg_duration=Avg(
            ExpressionWrapper(F('duration'), output_field=fields.DurationField()) / 3600000000  # Convert microseconds to hours
        )
    ).order_by('severity'))
    
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
        'duration_by_severity': duration_by_severity,
        'yearly_trend': yearly_trend
    }
    
    return JsonResponse(data)


# For AJAX chart data
@login_required
def incident_chart_data(request):
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
    
    data = {
        'months': months,
        'counts': counts,
        'severity_labels': severity_labels,
        'severity_counts': severity_counts,
    }
    
    return JsonResponse(data)

@login_required
def export_yearly_report(request, year):
    from openpyxl import Workbook
    from django.http import HttpResponse
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"Rapport {year}"
    
    # En-têtes
    headers = ['Month', 'Number of incidents', 'Resolution average time']
    ws.append(headers)
    
    # Données mensuelles
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
    
    # Préparation de la réponse
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=rapport_incidents_{year}.xlsx'
    
    wb.save(response)
    return response

def dashboard(request):
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
    return render(request, 'incidents/dashboard.html', context)