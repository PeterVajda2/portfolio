from django import template
from maintenance.models import Part, SpareParts

register = template.Library()

@register.simple_tag
def get_attribute(part, attribute, *is_boolean):
    if hasattr(part, attribute):
        return_value = getattr(part, attribute.lower())
    else:
        return_value = getattr(part.part, attribute.lower())

    if return_value is None:
        return_value = ''

    if is_boolean and return_value == '':
        return_value = "false"

    return return_value

@register.simple_tag(takes_context=True)
def visible_for_user(context, column):
    if column.uservisible_set.filter(user=context['request'].user, column=column, visible=True).exists():
        return "checked"

@register.filter
def get_label_cz(columns):
    return_list = []
    for c in columns:
        return_list.append(c.label_cz)
    
    return return_list