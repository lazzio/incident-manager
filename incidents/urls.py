from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.IncidentListView.as_view(), name='incident_list'),
    path('incident/<int:pk>/', views.IncidentDetailView.as_view(), name='incident_detail'),
    path('incident/new/', views.create_incident, name='incident_create'),
    path('incident/<int:pk>/edit/', views.update_incident, name='incident_update'),
    path('incident/<int:pk>/delete/', views.IncidentDeleteView.as_view(), name='incident_delete'),
    path('incident/<int:pk>/add-update/', views.add_incident_update, name='add_incident_update'),
    path('incident/<int:pk>/add-comment/', views.add_comment, name='add_comment'),  # URL corrigée
    path('timeline/', views.IncidentTimelineView.as_view(), name='incident_timeline'),
    path('report/', views.yearly_report, name='yearly_report'),
    path('report/<int:year>/export/', views.export_yearly_report, name='export_yearly_report'),
    path('api/chart-data/', views.incident_chart_data, name='incident_chart_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
]