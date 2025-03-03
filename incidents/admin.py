from django.contrib import admin
from .models import Incident, IncidentFile, IncidentLink, IncidentUpdate


@admin.register(Incident, IncidentFile, IncidentLink, IncidentUpdate)
class IncidentAdmin(admin.ModelAdmin):
    pass

class IncidentFileAdmin(admin.ModelAdmin):
    pass

class IncidentLinkAdmin(admin.ModelAdmin):
    pass

class IncidentUpdateAdmin(admin.ModelAdmin):
    pass
