from django import template
import calendar
from calendar import different_locale
from django.utils import translation
import locale
import unidecode
from django.db.models import Sum, Count
from burza.models import CostCenter, Worker, Assignment

register = template.Library()

@register.filter
def month_name(month_number, locale="cs_CZ"):
    with different_locale(locale):
        return calendar.month_name[month_number].capitalize()


@register.simple_tag(takes_context=True)
def month_name2(context, month_number, locale="cs_CZ.UTF-8"):

    if locale == 'cs':
        locale = 'cs_CZ.utf8'
    else:
        locale = 'en_US.utf8'

    with different_locale(locale):
        return calendar.month_name[month_number].capitalize()


@register.simple_tag(takes_context=True)
def day_abbrev(context, day_number, locale="en-us"):

    if locale == 'cs':
        locale = 'cs_CZ.utf8'
    else:
        locale = 'en_US.utf8'

    with different_locale(locale):
        return calendar.day_name[day_number].capitalize()

@register.filter
def strip_accents(phrase):
    return unidecode.unidecode(phrase)

@register.filter(name='range')
def filter_range(start, end):
    return range(start, end)


@register.filter
def get_value_list_of_fullfiled(source_dict):
    list_return = []
    try:
        for key, value in source_dict.items():
            for key2, value2 in value.items():
                if key2 == 'fullfiled':
                    list_return.append(value2)
        return list_return
    except:
        return list_return

@register.filter
def get_value_list_of_unfullfiled(source_dict):
    list_return = []
    try:
        for key, value in source_dict.items():
            for key2, value2 in value.items():
                if key2 == 'unfullfiled':
                    list_return.append(value2)

        return list_return
    except:
        return list_return


@register.filter
def get_value_list_target(source_dict):
    list_return = []
    try:
        for key, value in source_dict.items():
            for key2, value2 in value.items():
                if key2 == 'target':
                    list_return.append(value2)

        return list_return
    except:
        return list_return

@register.filter
def shift_to_hour(shifts):
    try:
        return shifts * 7.5
    except:
        return 0


@register.filter
def in_hours(list_of_shifts):
    new_list = []

    for item in list_of_shifts:
        new_list.append(item * 7.5)

    return new_list

@register.filter
def comma_to_dot(number):

    return str(number).replace(',','.')

@register.filter
def edit30(duration):
    
    if duration < 8:
        return duration
    else:
        return duration - 0.5

@register.filter
def used_verbed(qs):
    if qs.count() == 1:
        return "Výpůjčka"
    elif qs.count() < 5:
        return "Výpůjčky"
    else:
        return "Výpůjček"


@register.filter
def hours(qs):
    hours = 0

    for item in qs:
        if item.hours == 8:
            hours += 7.5
        else:
            hours += item.hours

    return hours


@register.filter
def top_target(qs, position):

    costcenters_id = set()
    result = {}

    for iqs in qs:
        costcenters_id.add(iqs.target_costcenter_id)

    for costcenter_id in costcenters_id:
        result[costcenter_id] = 0

    for iqs in qs:
        result[iqs.target_costcenter_id] += 1

    result_sorted = {key: value for (key, value) in sorted(result.items(), key=lambda tup: tup[1], reverse=True)}

    try:
        costcenter_id = list(result_sorted.keys())[int(position)-1]
        costcenter_qty = result_sorted[costcenter_id]

        text = str(CostCenter.objects.values_list('name', flat=True).get(id=costcenter_id))

        return '[' + str(costcenter_qty) + '] ' + text
    except:
        return None


@register.filter
def top_source(qs, position):

    workers = {}
    cost_centers = {}

    for item_qs in qs:
        if not item_qs.worker_id in workers:
            workers[item_qs.worker_id] = 1
        else:
            workers[item_qs.worker_id] += 1

    for worker, qty in workers.items():
        worker_costcenter = Worker.objects.values_list('costcenter__name', flat=True).get(id=worker)
        if not worker_costcenter in cost_centers:
            cost_centers[worker_costcenter] = qty
        else:
            cost_centers[worker_costcenter] += qty

    cost_centers_sorted = {key: value for (key, value) in sorted(cost_centers.items(), key=lambda tup: tup[1], reverse=True)}

    try:
        costcenter = list(cost_centers_sorted.keys())[int(position)-1]
        costcenter_qty = cost_centers_sorted[costcenter]
        text = str(costcenter)
        
        return '[' + str(costcenter_qty) + '] ' + text
    except:
        return None


@register.filter
def top_request(d, position):

    def take_second(elem):
        return elem[1]['wanted']

    results_sorted = [(costcenter_id) for costcenter_id in sorted(d.items(), key=take_second, reverse=True)]
    
    results_named = {CostCenter.objects.values_list('name', flat=True).get(id=costcenter_id): value for (costcenter_id, value) in dict(results_sorted).items()}

    try:
        return list(results_named.items())[int(position)]
    except:
        return None


@register.filter
def offers_to_add(received_tuple, offers_qs):

    list_of_offer_ids = []

    try:
        costcenter = received_tuple[0]
    except:
        return None

    costcenter_id = CostCenter.objects.values_list('id', flat=True).get(name=costcenter)

    for offer in offers_qs:
        list_of_offer_ids.append(offer.id)

    try:
        trt = list(Assignment.objects.filter(offer_id__in=list_of_offer_ids, target_costcenter_id=costcenter_id).values_list('hours', flat=True))[0]
    except:
        trt = 0

    received_tuple[1]['got'] += trt

    return received_tuple
    


@register.filter
def returnitem(lst, position):
    try:
        return lst[position]
    except:
        return None


@register.filter
def value_by_key(dict, key):
    try:
        return dict[key]
    except:
        return None

