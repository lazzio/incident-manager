from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr):
    """Gets an attribute of an object dynamically from a string name"""
    if hasattr(obj, attr):
        return getattr(obj, attr)
    elif hasattr(obj, 'get') and callable(obj.get):
        # Handle dictionaries
        try:
            return obj.get(attr)
        except (TypeError, KeyError):
            pass
    
    # Support for nested attributes: user.profile.name
    if '.' in attr:
        parts = attr.split('.')
        part = parts[0]
        if hasattr(obj, part):
            remaining = '.'.join(parts[1:])
            return get_attr(getattr(obj, part), remaining)
    
    # Default to empty string if attribute doesn't exist
    return ""
