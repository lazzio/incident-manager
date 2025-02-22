# incident_manager/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('incidents.urls')),  # Inclut les URLs de l'application incidents
    
    # URLs d'authentification
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    path('favicon.ico', RedirectView.as_view(url='/static/incidents/img/favicon.ico')),
]

# Configuration pour servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personnalisation de l'interface d'administration
admin.site.site_header = "Gestion des Incidents - Administration"
admin.site.site_title = "Gestion des Incidents"
admin.site.index_title = "Tableau de bord d'administration"
