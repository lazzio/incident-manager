from django.contrib import admin
from .models import Incident, IncidentAttachment, IncidentLink, IncidentUpdate


@admin.register(Incident, IncidentAttachment, IncidentLink, IncidentUpdate)
class IncidentAdmin(admin.ModelAdmin):
    pass

class IncidentAttachmentAdmin(admin.ModelAdmin):
    pass

class IncidentLinkAdmin(admin.ModelAdmin):
    pass

class IncidentUpdateAdmin(admin.ModelAdmin):
    pass
