from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Action, Profile, News, NewsItem, PendingDoi
import datetime
from django.db.models import Sum
from datetime import date, datetime
from django.contrib import messages
from django.conf import settings
from django.db.models import Avg
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
import re


@login_required
def add_action(request, currency="CZK"):

    context = {
    }

    context['currency'] = currency

    if request.method == 'POST':
        context['departments'] = list(Action.objects.all().values_list('type').distinct('type'))
        specs = {}
        for key, value in dict(request.POST).items():
            if value[0]:
                specs[key] = value[0]
        try:
            specs['savings_actual_year'] = int(specs['savings_actual_year'].replace(" ", ""))
            if currency == "EUR":
                specs['savings_actual_year'] = specs['savings_actual_year'] * settings.EUR_EX
        except:
            pass
        
        try:
            specs['savings_per_year'] = int(specs['savings_per_year'].replace(" ", ""))
            if currency == "EUR":
                specs['savings_per_year'] = specs['savings_per_year'] * settings.EUR_EX
        except:
            pass

        specs['created_by'] = request.user
        
        specs.pop('csrfmiddlewaretoken')
        specs.pop('Add action')

        newAction = Action.objects.update_or_create(**specs)

        add_to_news(newAction, "new action")

        text = 'Action was added'
        messages.add_message(request, messages.INFO, text)

    if request.method == 'GET':
        context['departments'] = list(Action.objects.all().values_list('type').distinct('type'))

    return render(request, 'add_action.html', context)

@login_required
def edit_action(request, action_id, currency="CZK"):

    context = {
    }

    context['currency'] = currency

    context['departments'] = list(Action.objects.all().values_list('type').distinct('type'))

    if request.method == 'POST':
        specs = {}
        for key, value in dict(request.POST).items():
            if value[0]:
                specs[key] = value[0]

        try:
            specs['savings_actual_year'] = int(specs['savings_actual_year'].replace(" ", ""))
            if currency == "EUR":
                specs['savings_actual_year'] = specs['savings_actual_year'] * settings.EUR_EX
        except:
            pass
        
        try:
            specs['savings_per_year'] = int(specs['savings_per_year'].replace(" ", ""))
            if currency == "EUR":
                specs['savings_per_year'] = specs['savings_per_year'] * settings.EUR_EX
        except:
            pass

        specs.pop('csrfmiddlewaretoken')
        specs.pop('Edit action')

        previousStateOfAction = Action.objects.values().get(id=action_id)

        print(request.user.profile.department)

        if int(specs['doi']) > 2 and not request.user.profile.department == 'FiCo':
            pending_doiObject = PendingDoi.objects.update_or_create(action=Action.objects.get(id=action_id), defaults={'previous_doi' : Action.objects.values_list('doi', flat=True).get(id=action_id), 'new_doi' : int(specs['doi'])})
            specs['doi'] = 2
    
        Action.objects.filter(id=action_id).update(**specs)

        newStateOfAction = Action.objects.values().get(id=action_id)

        changed_attributes = {}

        for k, v in previousStateOfAction.items():
            if not newStateOfAction[k] == v:
                changed_attributes[k] = {}
                changed_attributes[k]['previous'] = v
                changed_attributes[k]['new'] = newStateOfAction[k]
        
        add_to_news(Action.objects.get(id=action_id), "edit action", changed_attributes)

        text = 'Action was changed'
        messages.add_message(request, messages.INFO, text)
        actionObject = Action.objects.get(id=action_id)
        context['action'] = actionObject

    if request.method == 'GET':
        actionObject = Action.objects.get(id=action_id)
        context['action'] = actionObject


    return render(request, 'edit_action.html', context)


def edit_multiple_actions(request):
    if request.method == 'POST':
        pass

    if request.method == 'GET':
        pass

    context = {

    }

    return render(request, 'edit_multiple_actions.html', context)


def show_single_action(request, action_id):
    if request.method == 'POST':
        pass

    if request.method == 'GET':
        pass

    context = {

    }

    return render(request, 'show_single_action.html', context)


def show_actions(request, currency='CZK'):

    context = {
    }

    context['labels'] = [piece[0] for piece in Action.objects.values_list('doi').distinct('doi')]
    context['savings_per_doi'] = [list(Action.objects.filter(doi=label).aggregate(Sum('savings_per_year')).values())[0] for label in context['labels']]
    context['today'] = date.today()
    context['currency'] = currency
    context['annual_savings_sum'] = list(Action.objects.all().aggregate(Sum('savings_per_year')).values())[0]
    context['actual_savings_sum'] = list(Action.objects.all().aggregate(Sum('savings_actual_year')).values())[0]
    context['count_of_actions'] = len(list(Action.objects.all()))
    context['average_doi'] = Action.objects.all().aggregate(average_doi=Avg('doi'))

    if request.method == 'POST':
        pass

    if request.method == 'GET':
        context['Actions'] = Action.objects.all()

    if request.user.is_authenticated:
        context['User'] = request.user

    if request.user.is_authenticated:
        news_object = News.objects.get(user=request.user)
        unread_items = news_object.newsitem_set.filter(read=False)

        context['unread_items'] = unread_items.count()
    else:
        context['unread_items'] = 0


    return render(request, 'show_actions.html', context)

def show_charts(request, currency='CZK'):

    context = {}
    pie_chart_data = [[{'v': str(X[0])}, int(list(Action.objects.filter(doi=X[0]).aggregate(Sum('savings_actual_year')).values())[0])] for X in list(Action.objects.values_list('doi').distinct('doi'))]
    labels = []
    labels.append('Degree of Implementation')
    labels = labels + list(Action.objects.all().values_list('type', flat=True).distinct('type'))
    context['labels'] = labels
    context['total'] = list(Action.objects.all().aggregate(Sum('savings_actual_year')).values())[0]

    dois = []

    list_of_dois = list(Action.objects.all().values_list('doi', flat=True).distinct('doi').order_by('doi'))

    for doi in list_of_dois:
        doi = str(doi)
        dois.append(getDoiValuesListPerDepartment(doi, labels[1:], currency))

    if currency == 'EUR':
        for item in dois:
            for i in range(1, len(item)):
                item[i] = item[i] / settings.EUR_EX

    context['dois'] = dois
    context['User'] = request.user

    if currency == 'EUR':
        for item in pie_chart_data:
            item[1] = int(item[1] / settings.EUR_EX)

    list_of_months = ['2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01', '2020-05-01', '2020-06-01', '2020-07-01', '2020-08-01', '2020-09-01', '2020-10-01', '2020-11-01', '2020-12-01']
    savings_per_month = {}

    i = 0
    for date in list_of_months:
        i = i+1
        savings_per_month[i] = getMonthlySavings(date)

    context['departments'] = list(Action.objects.all().values_list('type', flat=True).distinct('type').order_by('type'))
    savings = {}

    if currency == 'EUR':
        for department in context['departments']:
            savings[department] = list(Action.objects.filter(type=department).aggregate(Sum('savings_actual_year')).values())[0] / settings.EUR_EX

    else:
        for department in context['departments']:
            savings[department] = list(Action.objects.filter(type=department).aggregate(Sum('savings_actual_year')).values())[0]

    dept_targets = {
        "Facility": 2162722,
        "FiCo": 1495689,
        "HR": 3283205,
        "IE": 661255,
        "IT": 100000,
        "MD": 5426528,
        "Operations": 5415203,
        "QD": 1462414,
        "SC": 29265305,
        "SM": 451910,
        "total": 49724231,
    }

    new_waterfall = {}
    total_sum = 0
    new_waterfall['total'] = {}
    new_waterfall['total']['t1'] = [0]
    new_waterfall['total']['t2'] = []
    new_waterfall['total']['t3'] = []
    new_waterfall['total']['t4'] = []
    new_waterfall['total']['t5'] = []
    new_waterfall['total']['x_data'] = []
    new_waterfall['total']['y_data'] = []
    new_waterfall['total']['text_list'] = []

    for key in dept_targets:
        if not key == "total":
            if currency == "EUR":
                dept_sum = sum(list(Action.objects.filter(type=key).values_list('savings_actual_year', flat=True))) / settings.EUR_EX
            else:
                dept_sum = sum(list(Action.objects.filter(type=key).values_list('savings_actual_year', flat=True)))
            total_sum += dept_sum
            new_waterfall['total']['y_data'].append(0.99 * total_sum)
            new_waterfall['total']['t2'].append(round(dept_sum))
            new_waterfall['total']['t1'].append(total_sum)
            new_waterfall['total']['t5'].append(0)
            new_waterfall['total']['x_data'].append(key)
            new_waterfall['total']['t3'].append(0)
            new_waterfall['total']['t4'].append(0)
            new_waterfall['total']['text_list'].append((f'{round(dept_sum):,}').replace(",", " "))
            
    new_waterfall['total']['t5'].append(0)
    if currency == "EUR":
        new_waterfall['total']['t5'].append(dept_targets['total']/ settings.EUR_EX)
    else:
        new_waterfall['total']['t5'].append(dept_targets['total'])
    new_waterfall['total']['t1'].pop()

    if currency == "EUR":
        if total_sum <= dept_targets['total'] / settings.EUR_EX:
            new_waterfall['total']['t3'].append((dept_targets['total'] / settings.EUR_EX) - total_sum)
            new_waterfall['total']['t4'].append(0)
            new_waterfall['total']['text_list'].append((f'{round(((dept_targets["total"] / settings.EUR_EX) - total_sum)):,}').replace(",", " "))
            new_waterfall['total']['t1'].append(total_sum)
            new_waterfall['total']['y_data'].append(0.97 * (dept_targets["total"] / settings.EUR_EX))
            new_waterfall['total']['x_data'].append('Under')

        else:
            new_waterfall['total']['t4'].append(total_sum - (dept_targets['total'] / settings.EUR_EX))
            new_waterfall['total']['t3'].append(0)
            new_waterfall['total']['text_list'].append((f'{(round(total_sum - (dept_targets["total"] / settings.EUR_EX))):,}').replace(",", " "))
            new_waterfall['total']['t1'].append(dept_targets['total'] / settings.EUR_EX)
            new_waterfall['total']['y_data'].append(1.05 * (dept_targets['total'] / settings.EUR_EX))
            new_waterfall['total']['x_data'].append('Over')
    else:
        if total_sum <= dept_targets['total']:
            new_waterfall['total']['t3'].append(dept_targets['total'] - total_sum)
            new_waterfall['total']['t4'].append(0)
            new_waterfall['total']['text_list'].append((f'{round((dept_targets["total"]- total_sum)):,}').replace(",", " "))
            new_waterfall['total']['t1'].append(total_sum)
            new_waterfall['total']['y_data'].append(0.97 * dept_targets["total"])
            new_waterfall['total']['x_data'].append('Under')

        else:
            new_waterfall['total']['t4'].append(total_sum - dept_targets['total'])
            new_waterfall['total']['t3'].append(0)
            new_waterfall['total']['text_list'].append((f'{(round(total_sum - dept_targets["total"])):,}').replace(",", " "))
            new_waterfall['total']['t1'].append(dept_targets['total'])
            new_waterfall['total']['y_data'].append(1.05 * dept_targets['total'])
            new_waterfall['total']['x_data'].append('Over')

    if currency == "EUR":
        new_waterfall['total']['text_list'].append(f'{round((dept_targets["total"]/settings.EUR_EX)):,}'.replace(",", " "))
        new_waterfall['total']['y_data'].append(0.97 * (dept_targets['total'] / settings.EUR_EX))
    else:
        new_waterfall['total']['text_list'].append(f'{round(dept_targets["total"]):,}'.replace(",", " "))
        new_waterfall['total']['y_data'].append(0.97 * dept_targets['total'])

    new_waterfall['total']['x_data'].append('Target')
    
    for key, value in dept_targets.items():
        if not key == "total":
            new_waterfall[key] = {}

    for key, value in new_waterfall.items():
        if not key == "total":
            total_sum = 0
            new_waterfall[key]['t1'] = [0]
            new_waterfall[key]['t2'] = []
            new_waterfall[key]['t3'] = []
            new_waterfall[key]['t4'] = []
            new_waterfall[key]['t5'] = []
            new_waterfall[key]['x_data'] = []
            new_waterfall[key]['y_data'] = []
            new_waterfall[key]['text_list'] = []
            saving_actions = Action.objects.filter(type=key).exclude(savings_actual_year=0).order_by('-savings_actual_year')

            for saving_action in saving_actions:
                if currency == "EUR":
                    total_sum += saving_action.savings_actual_year / settings.EUR_EX
                else:
                    total_sum += saving_action.savings_actual_year
                new_waterfall[key]['y_data'].append(0.99 * total_sum)

                if currency == "EUR":
                    new_waterfall[key]['t2'].append(round(saving_action.savings_actual_year / settings.EUR_EX))
                    new_waterfall[key]['text_list'].append((f'{round(saving_action.savings_actual_year / settings.EUR_EX):,}').replace(",", " "))
                else:
                    new_waterfall[key]['t2'].append(round(saving_action.savings_actual_year))
                    new_waterfall[key]['text_list'].append((f'{round(saving_action.savings_actual_year):,}').replace(",", " "))

                new_waterfall[key]['t1'].append(total_sum)
                new_waterfall[key]['t5'].append(0)
                new_waterfall[key]['x_data'].append(break_it(shorten_it(saving_action.name)))
                new_waterfall[key]['t3'].append(0)
                new_waterfall[key]['t4'].append(0)

            new_waterfall[key]['t5'].append(0)
            if currency == "EUR":
                new_waterfall[key]['t5'].append(dept_targets[key]/ settings.EUR_EX)
            else:
                new_waterfall[key]['t5'].append(dept_targets[key])
            new_waterfall[key]['t1'].pop()
            
            if currency == "EUR":
                if total_sum <= (dept_targets[key] / settings.EUR_EX):
                    new_waterfall[key]['t3'].append((dept_targets[key] / settings.EUR_EX) - total_sum)
                    new_waterfall[key]['t4'].append(0)
                    new_waterfall[key]['text_list'].append((f'{round(((dept_targets[key] / settings.EUR_EX)- total_sum)):,}').replace(",", " "))
                    new_waterfall[key]['t1'].append(total_sum)
                    new_waterfall[key]['y_data'].append(0.97 * (dept_targets[key] / settings.EUR_EX))
                    new_waterfall[key]['x_data'].append('Under')
                else:
                    new_waterfall[key]['t4'].append(total_sum - (dept_targets[key] / settings.EUR_EX))
                    new_waterfall[key]['t3'].append(0)
                    new_waterfall[key]['text_list'].append((f'{(round(total_sum - (dept_targets[key] / settings.EUR_EX))):,}').replace(",", " "))
                    new_waterfall[key]['t1'].append(dept_targets[key] / settings.EUR_EX)
                    new_waterfall[key]['y_data'].append(1.05 * (dept_targets[key] / settings.EUR_EX))
                    new_waterfall[key]['x_data'].append('Over')
            else:
                if total_sum <= dept_targets[key]:
                    new_waterfall[key]['t3'].append(dept_targets[key] - total_sum)
                    new_waterfall[key]['t4'].append(0)
                    new_waterfall[key]['text_list'].append((f'{round((dept_targets[key] - total_sum)):,}').replace(",", " "))
                    new_waterfall[key]['t1'].append(total_sum)
                    new_waterfall[key]['y_data'].append(0.97 * dept_targets[key])
                    new_waterfall[key]['x_data'].append('Under')
                else:
                    new_waterfall[key]['t4'].append(total_sum - dept_targets[key])
                    new_waterfall[key]['t3'].append(0)
                    new_waterfall[key]['text_list'].append((f'{(round(total_sum - dept_targets[key])):,}').replace(",", " "))
                    new_waterfall[key]['t1'].append(dept_targets[key])
                    new_waterfall[key]['y_data'].append(1.05 * dept_targets[key])
                    new_waterfall[key]['x_data'].append('Over')

            new_waterfall[key]['x_data'].append('Target')

            if currency == "EUR":
                new_waterfall[key]['text_list'].append(f'{round(dept_targets[key] / settings.EUR_EX):,}'.replace(",", " "))
                new_waterfall[key]['y_data'].append(0.97 * (dept_targets[key] / settings.EUR_EX))
            else:
                new_waterfall[key]['text_list'].append(f'{dept_targets[key]:,}'.replace(",", " "))
                new_waterfall[key]['y_data'].append(0.97 * dept_targets[key])

        context.update({
        "pie_chart_data": pie_chart_data,
        "currency": currency,
        "savings_per_month": savings_per_month,
        "savings": savings,
        "new_waterfall": new_waterfall,
    })

    return render(request, 'show_charts.html', context)

def getDoiValuesListPerDepartment(doi, departments, currency='CZK'):

    doiList = []
    doiList.append(doi)
    for department in departments:
        doiList = doiList + list(Action.objects.filter(doi=doi, type=department).aggregate(Sum('savings_actual_year')).values())

    doiList = [0 if v is None else v for v in doiList]

    return doiList

def recalcActualYearSavings(request):

    for trt in Action.objects.all():
        trt.savings_actual_year = trt.savings_per_year * (months_until_eoy(trt.savings_start, trt.savings_till) / 12)
        trt.save()

def months_until_eoy(d2, d1):
    return int((d1.year - d2.year) * 12 + d1.month - d2.month + 1)


def recalcMonthlySavings(request):

    for object in Action.objects.all():
        if object.savings_per_year: 
            object.savings_per_month = object.savings_per_year / 12
            object.save()
        else:
            pass

def getMonthlySavings(date):
    
    return int(round(list(Action.objects.filter(savings_start__lte=date, savings_till__gte=date).aggregate(Sum('savings_per_year')).values())[0]/12))


def add_to_news(change, type, *args):

    users = User.objects.all()

    if args:
        text_to_add = {}
        for k, v in args[0].items():
            text_to_add[k] = {}
            for k2, v2 in v.items():
                text_to_add[k][k2] = str(v2)

    if type == "new action":
        for user in users:
            newsobject = News.objects.update_or_create(user=user)
            newitem = NewsItem.objects.create(type="New action", action=change[0], text="Dummy", date=date.today())
            newitem.news.add(newsobject[0])

    if type == "edit action":
        for user in users:
            newsobject = News.objects.update_or_create(user=user)
            newitem = NewsItem.objects.create(type="Edit action", action=change, text=text_to_add, date=date.today())
            newitem.news.add(newsobject[0])
        
    return None


def show_news(request):

    if request.user.is_authenticated:
        try:
            news_object = News.objects.get(user=request.user)
        except:
            context = {}
            return render(request, 'news.html', context)
        
        unread_items = news_object.newsitem_set.filter(read=False).order_by('type')
        read_items = news_object.newsitem_set.filter(read=True).order_by('type')

        pending_doi_changes = PendingDoi.objects.all()

        context = {
            'unread_items': unread_items,
            'read_items': read_items,
            'pending_doi_changes': pending_doi_changes,
        }

        if not unread_items and not read_items:
            context = {'info': "No new items"}

        return render(request, 'news.html', context)

    else:
        context = {'info': "User is not logged in"}
        return render(request, 'news.html', context)


def read_news(request):

    news_object = News.objects.get(user=request.user)
    unread_items = news_object.newsitem_set.filter(read=False)

    for unread_item in unread_items:
        unread_item.read = True
        unread_item.save()

    return HttpResponse("OKAY")


def doi_change_agree(request, action_id, doi):

    actionObject = Action.objects.get(id=action_id)
    actionObject.doi = doi
    actionObject.save()

    pending_doi_changeObject = PendingDoi.objects.get(action=actionObject)
    pending_doi_changeObject.delete()

    return redirect('show_news')


def break_it(string, sub=" ", wanted="<br>", n=2):

    count_of_spaces = string.count(' ')
    if count_of_spaces > 4:
        n = round(count_of_spaces/2)
        where = [m.start() for m in re.finditer(sub, string)][n-1]
        before = string[:where]
        after = string[where:]
        after = after.replace(sub, wanted, 1)
        newString = before + after
        return newString
    else:
        return string

def shorten_it(string):

    newString = (string[:74] + '..') if len(string) > 74 else string
    return newString
