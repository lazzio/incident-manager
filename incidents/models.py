from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings
import os
from django_quill.fields import QuillField

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
    details = QuillField()
    resolution_process = QuillField()
    impact = QuillField()
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


class Comment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        # Call the original save method to save the comment
        super().save(*args, **kwargs)
        
        # Update the incident's updated_at field
        # Note: This will trigger the incident's save method as well
        self.incident.save(update_fields=['updated_at'])
        
    def __str__(self):
        return f"Comment on {self.incident.title} at {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']


class IncidentFile(models.Model):
    incident = models.ForeignKey('Incident', on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='incident_files/%Y/%m/')
    filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                   null=True, related_name='uploaded_files')

    def __str__(self):
        return f"File {self.filename} for incident #{self.incident.id}"
    
    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
    
    @property
    def is_image(self):
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml', 'image/bmp']
        return self.content_type in image_types
    
    @property
    def file_icon(self):
        if self.is_image:
            return 'fa-file-image'
        elif 'pdf' in self.content_type:
            return 'fa-file-pdf'
        elif 'word' in self.content_type or 'office' in self.content_type:
            return 'fa-file-word'
        elif 'excel' in self.content_type or 'spreadsheet' in self.content_type:
            return 'fa-file-excel'
        elif 'zip' in self.content_type or 'compressed' in self.content_type:
            return 'fa-file-zipper'
        elif 'text' in self.content_type:
            return 'fa-file-alt'
        else:
            return 'fa-file'