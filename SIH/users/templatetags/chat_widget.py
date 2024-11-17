from django import template

register = template.Library()

@register.inclusion_tag('users/chat_widget.html')
def chat_widget():
    return {} 