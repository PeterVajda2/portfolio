from django import template
import re
from django.conf import settings

register = template.Library()

@register.filter
def number_if_available(object):
    if not str(object).isdigit():
        if str(object).replace('.','').replace(',','').isdigit():
            return int(str(object)[:-2])
        else:
            return object
    else:
        return int(object)

@register.filter 
def verbose_name(object): 
    if object == 'type':
        return 'Department'
    if object == 'name':
        return 'Name'
    if object == 'responsible':
        return 'Responsible'
    if object == 'savings_start':
        return 'Savings start'
    if object == 'savings_till':
        return 'Savings valid until'
    if object == 'savings_per_month':
        return 'Savings per month'
    if object == 'savings_per_year':
        return 'Savings per year'
    if object == 'savings_actual_year':
        return 'Savings in actual year'
    if object == 'doi':
        return 'DoI'
    if object == 'comments':
        return 'Comments'

@register.filter
def in_eur(amount):
    if amount:
        if is_number(amount):
            pass
        else:
            list_amount = amount.split(',| ')
            amount = ''.join(list_amount)
        return float(amount) / settings.EUR_EX
    else:
        return amount

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
@register.filter
def separated(amount):
    if is_number(amount):
        amount3 = f'{int(amount):,}'
        stringed = str(amount3)
        listed = stringed.split(',')
        joined = ' '.join(listed)
        return joined
