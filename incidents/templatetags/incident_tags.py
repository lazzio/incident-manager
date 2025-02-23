from django import template

register = template.Library()

@register.filter
def abs_filter(value):
    """Returns the absolute value of a number"""
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value
