from django import template
import json

register = template.Library()

@register.filter(name='json')
def json_filter(value):
    return json.dumps(value, indent=2)

@register.filter(name='newline_join')
def newline_join(value):
    if isinstance(value, list):
        return '\n'.join(value)
    return value
