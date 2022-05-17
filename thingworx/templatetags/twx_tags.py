from django import template
import json

register = template.Library()

@register.filter
def make_machine_name(raw_string):
    new_string = raw_string.replace('MachineThing', '').replace('StationThing', '').replace('KBLIB', '')
    return new_string

@register.simple_tag
def get_color_from_difference(compared_time, apo_time):
    if compared_time > 1.2 * apo_time:
        return str('style="background-color: rgba(255,0,0,0.9)"')
    elif compared_time > 1.1 * apo_time:
        return str('style="background-color: rgba(255,255,0,0.9)"')
    elif compared_time < 1.1 * apo_time:
        return str('style="background-color: rgba(0,255,0,0.9)"')


@register.filter
def get_tuples_0(list_of_tuples):
    return [tup[0] for tup in list_of_tuples]

    
@register.simple_tag
def adjust_name(orig_string, *args):


    for arg in args:
        new_string = orig_string.replace(arg,'')
        orig_string = new_string

    return new_string


@register.filter
def get_labels(data_list):

    labels = []

    for item in data_list:
        labels.append(item[0])

    return labels

@register.filter
def get_values(data_list):

    labels = []

    for item in data_list:
        labels.append(item[2])

    return labels