from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary safely."""
    try:
        return dictionary.get(str(key)) or dictionary.get(int(key))
    except (KeyError, AttributeError, ValueError):
        return None