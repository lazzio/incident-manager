from django.urls import path
from . import views
from .pkg_views import (
    incidents_list,
    incidents_detail,
    incidents_upsert,
    incidents_delete,
    incidents_timeline,
    incidents_dashboard,
    incidents_yearly_report,
)

urlpatterns = [
    path('dashboard/', incidents_dashboard.dashboard, name='dashboard'),
    path('incidents/', incidents_list.IncidentListView.as_view(), name='incident_list'),
    path('incident/<int:pk>/', incidents_detail.IncidentDetailView.as_view(), name='incident_detail'),
    path('incident/new/', incidents_upsert.create_incident, name='incident_create'),
    path('incident/<int:pk>/edit/', incidents_upsert.update_incident, name='incident_update'),
    path('incident/<int:pk>/delete/', incidents_delete.IncidentDeleteView.as_view(), name='incident_delete'),
    path('incident/<int:pk>/add-update/', incidents_upsert.add_incident_update, name='add_incident_update'),
    path('incident/<int:pk>/add-comment/', incidents_upsert.add_comment, name='add_comment'),
    path('timeline/', incidents_timeline.IncidentTimelineView.as_view(), name='incident_timeline'),
    path('report/', incidents_yearly_report.yearly_report, name='yearly_report'),
    path('report/<int:year>/export/', incidents_yearly_report.export_yearly_report, name='export_yearly_report'),
    path('api/chart-data/', incidents_yearly_report.incident_chart_data, name='incident_chart_data'),
]