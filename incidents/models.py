from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings

class Severity(models.TextChoices):
    CRITICAL = 'CRITICAL', _('Critical')
    HIGH = 'HIGH', _('High')
    MEDIUM = 'MEDIUM', _('Medium')
    LOW = 'LOW', _('Low')

class Category(models.TextChoices):
    CATEGORIE = 'categorie', 'Catégorie'
    AUTRE = 'autre', 'Autre'

class Incident(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    title = models.CharField(max_length=200)
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    details = models.TextField()
    resolution_process = models.TextField()
    impact = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_incidents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Status'
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.CATEGORIE
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents'
    )
    
    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.duration = self.end_date - self.start_date
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()}) - {self.start_date.strftime('%Y-%m-%d')}"
    
    def get_absolute_url(self):
        return reverse('incident_detail', kwargs={'pk': self.pk})
    
    class Meta:
        ordering = ['-start_date']


class IncidentAttachment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='incident_attachments/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for {self.incident.title}"


class IncidentLink(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()
    title = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title


class IncidentUpdate(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='updates')
    timestamp = models.DateTimeField(auto_now_add=True)
    update_text = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Update for {self.incident.title} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']