from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary safely.
    Handles both regular dictionary lookups and User objects as keys.
    """
    if isinstance(key, User):
        return dictionary.get(key)
    try:
        if isinstance(dictionary, dict):
            return dictionary.get(str(key)) or dictionary.get(int(key))
        return None
    except (KeyError, AttributeError, ValueError):
        return None