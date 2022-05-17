from django import template

register = template.Library()

@register.filter
def to_percent(value):
    return str(value * 100) + "%"