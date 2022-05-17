from django import template
from fp09.models import DowntimeFromLine

register = template.Library()

@register.simple_tag
def log_role(profile):
    if profile.role == "Logistics":
        return True
    return False


@register.simple_tag
def prod_role(profile):
    if profile.role == "Production":
        return True
    return False


@register.simple_tag
def cannot_edit_profile(user, profile):
    if user == profile.user:
        return False
    elif user.logistics_profile.is_admin:
        return False
    return True


@register.filter
def get_attribute(object, attribute):
    if attribute == 'user':
        return f"{object.user.last_name}, {object.user.first_name}"
    return getattr(object, attribute)


@register.simple_tag
def get_external_downtime(external_downtime_line, external_downtime_id):
    if external_downtime_line == 'FP09':
        downtime_object = DowntimeFromLine.objects.get(id=external_downtime_id)
        return {'category': downtime_object.category, 'subcategory': downtime_object.downtime}


@register.simple_tag
def is_parent(class_object):
    if 'child' in class_object:
        return True
    return False


@register.simple_tag
def is_deletable(class_object):
    if class_object['deletable']:
        return True
    return False


@register.simple_tag
def is_child(class_object):
    if 'parent' in class_object:
        return True
    return False


@register.simple_tag
def is_editable(class_object):
    if class_object['editable']:
        return True
    return False


@register.simple_tag
def is_addable(class_object):
    if class_object['addable']:
        return True
    return False


@register.simple_tag
def responsible_for_area(profile, production_area):
    if profile in production_area.responsible.all():
        return True
    return False