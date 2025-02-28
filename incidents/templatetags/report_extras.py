from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtracts the arg from the value."""
    try:
        return value - arg
    except (ValueError, TypeError):
        return value
    
@register.filter
def percentage_of(value, total):
    """Calculates percentage and formats it."""
    try:
        result = (value / total) * 100
        return round(result)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def filter_by_severity(severity_counts, severity_value):
    """Filters severity counts by severity value."""
    try:
        for item in severity_counts:
            if item['severity'] == severity_value:
                return [item]
        return []
    except Exception:
        return []

@register.filter
def sum_counts(severity_counts):
    """Sums the counts in a severity count queryset."""
    try:
        return sum(item['count'] for item in severity_counts)
    except Exception:
        return 0
