import os
from django import template
from django.conf import settings

register = template.Library()

@register.filter
def file_exists(file_obj):
    """
    Check if a file exists in the filesystem
    
    Usage: {{ file|file_exists }}
    """
    if not file_obj or not file_obj.path:
        return False
    
    return os.path.exists(file_obj.path)
