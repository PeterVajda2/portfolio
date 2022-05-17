from django import template
from reman.models import CC_material, FG_material

register = template.Library()


@register.filter
def get_cc_materials(fg_material_number):

    fg_materials = FG_material.objects.filter(material_number=fg_material_number)

    cc_material_numbers = []

    for fg_material in fg_materials:
        try:
            cc_material_numbers.append(fg_material.cc_material.material_number)
        except:
            pass

    return cc_material_numbers


@register.filter
def get_fg_material(data_dict):
    for fg_material, data in data_dict.items():
        return fg_material


@register.filter
def get_rr_disassembly(data_dict):
    for fg_material, data in data_dict.items():
        return data['regeneration_rate']


@register.filter
def list_to_string(list_of_items):
    return "<br />".join(list_of_items)


@register.filter
def queryset_to_list(qs):
    return list(qs.values_list('material_number', flat=True))


@register.filter
def string_to_int(string_num):
    if string_num:
        return float(string_num)
    else:
        return 0


@register.filter
def to_percentage(string_value, decimals):

    if string_value == '' or string_value == None:
        string_value = 0

    if int(decimals) > 0:
        return str(round(float(string_value) * 100, int(decimals))) + '%'
    else:
        return str(round(float(string_value) * 100)) + '%'


@register.simple_tag
def target_quantity(fg_material, cc_material, order_quantity):

    if CC_material.objects.filter(material_number=cc_material).exists():
        cc_material = CC_material.objects.get(material_number=cc_material)

        try:
            multiplicator = FG_material.objects.get(cc_material=cc_material, material_number=fg_material).multiplicator
        except:
            multiplicator = 0

        return multiplicator * order_quantity

    else:
        return 0