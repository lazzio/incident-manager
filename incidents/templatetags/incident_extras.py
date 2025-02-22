from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtract the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def percentage(value, total):
    """Calculate percentage of value to total."""
    try:
        return floatformat((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0