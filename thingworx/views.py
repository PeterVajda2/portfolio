from numbers import Number
from django.db.models.fields import DateTimeCheckMixin, FloatField
from django.shortcuts import render
from django.views.decorators import csrf
from .models import CMCanvas, CMElement, Infrastructure, MachinesConverter, MaterialConsumption, ProductionDataEdited, Smartkpi, PartNumber, Smartkpimachinestatusdata, Smartkpiorderkeyvaluedata, Smartkpimachinemessagedata, Smartkpiprocessfloatdata, OrderStart, Shiftcalendar, DLP3, PartNumberEffort, StandardLineOccupancy, ProductionGroup, OperatorsData, OperatorsDataEdited, ProductionBoxPlot, statisticaldata, TempSmartkpicvsproductiontargetdetail, OrdersPlanned, OrdersReality, NumberOfWorkersPlanned, Tb_fp09_alarms, FP09_alarm_description, Smartkpivalues, FP09_oee_manual_entries, LineFailureTranslation, NOKReasonsTranslation, ThingworxLocalmachinestatusdata, ThingworxLocalsmartkpi, DLP115min, DLP160min, DLP14hrs, CardReader
from fp09.models import TbFp09Qd
import datetime
import statistics
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from operator import itemgetter, mod, truediv
from collections import defaultdict 
from django.db.models import Sum, Count, Max, F, ExpressionWrapper, DateTimeField, DurationField, Q
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.core.files import File
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import math
import psycopg2
from django.core.files.storage import default_storage
from django.db.models.functions import Substr
import os
from django.db.models.functions import Trunc
from calendar import HTMLCalendar, MONDAY
from django.forms.models import model_to_dict
import paramiko
import time
import random
import requests
from operator import itemgetter
from statistics import median
import copy

def card_reader(request):
    if request.method == "POST":
        print(request)
    return "Done"

@csrf_exempt
def fp09_oee_manual_entries(request):

    entries = FP09_oee_manual_entries.objects.all()
    entries_json = []

    month = request.GET.get('month', datetime.date.today().month)

    for entry in entries:
        entry_dict = model_to_dict(entry)
        entry_dict['entry_date'] = datetime.datetime.strftime(entry_dict['entry_date'], '%Y-%m-%d')
        entries_json.append(entry_dict)


    hc = HTMLCalendar(MONDAY)
    str = hc.formatmonth(2021, int(month))

    if request.method == "POST":
        data = json.loads(request.body)

        if 'all' not in data and 'date' not in data:
            sampling_shift = data['sampling_shift'] if not data['sampling_shift'] == '---' else None
            repair_shift = data['repair_shift'] if not data['repair_shift'] == '---' else None
            station = data['station']
            what = data['what']
            a3 = True if data['a3'] == 'Ano' else False

            entry, updated = FP09_oee_manual_entries.objects.update_or_create(entry_date=data['entry_date'], defaults = {'sampling_shift' : sampling_shift, 'repair_shift': repair_shift, 'station' : station, 'what': what, 'a3': a3})

            return JsonResponse({'entry': model_to_dict(entry)})

        if 'all' in data:
            entries = FP09_oee_manual_entries.objects.all()
            entries_json = []

            for entry in entries:
                entry_dict = model_to_dict(entry)
                entry_dict['entry_date'] = datetime.datetime.strftime(entry_dict['entry_date'], '%Y-%m-%d')
                entries_json.append(entry_dict)
            
            return JsonResponse({'entries': entries_json})

        if 'date' in data:
            FP09_oee_manual_entries.objects.get(entry_date=data['date']).delete()
            
            return JsonResponse({'okay': 'okay'})


    return render(request, 'fp09_oee_manual.html', context = {'calendar': str, 'entries': json.dumps(entries_json), 'month': month})

@csrf_exempt
def fp09_oee(request):

    return render(request, 'fp09_oee.html', context = {})

@csrf_exempt
def fp09_oee_data(request):

    data = json.loads(request.body)

    range_to = datetime.date.today()
    range_from = range_to - datetime.timedelta(days = data['days']) - datetime.timedelta(days=1)
    range_from = datetime.datetime(range_from.year, range_from.month, range_from.day, 22, 0, 0)


    if 'adjusted' in data:

        excluded_shifts = FP09_oee_manual_entries.objects.all()

        list_of_excluded_shifts = []

        for shift in excluded_shifts:
            shift_date = shift.entry_date
            if shift.sampling_shift:
                sampling_shift_time_start = shift.sampling_shift
                sampling_shift_datetime_string = f'{shift_date} {sampling_shift_time_start[0:4]}'
                list_of_excluded_shifts.append(datetime.datetime.strptime(sampling_shift_datetime_string, '%Y-%m-%d %H:%M'))
            if shift.repair_shift:
                repair_shift_time_start = shift.repair_shift
                repair_shift_datetime_string = f'{shift_date} {repair_shift_time_start[0:4]}'
                list_of_excluded_shifts.append(datetime.datetime.strptime(repair_shift_datetime_string, '%Y-%m-%d %H:%M'))

        our_oee = list(Smartkpivalues.objects.filter(kpidatetime__gte=range_from, kpidatetime__lt=range_to, kpiname='CVS: OEE (Version 2)', machine='KBLIBFP09-Lanico2MachineThing', kpitimebase='shift').exclude(kpidatetime__in=list_of_excluded_shifts).values_list('kpidatetime', 'kpifloatvalue'))

        for idx, (dt, value) in enumerate(our_oee):
            if dt.hour == 22:
                our_oee[idx] = ((dt + datetime.timedelta(hours=2)).date(), value)
            else:
                our_oee[idx] = (dt.date(), value)


        calculated_days = {}
        
        for (dt, value) in our_oee:
            if dt not in calculated_days:
                calculated_days[dt] = {}
                calculated_days[dt]['value'] = value
                calculated_days[dt]['count'] = 1
            else:
                calculated_days[dt]['value'] += value
                calculated_days[dt]['count'] += 1

        for dt, value_dict in calculated_days.items():
            calculated_days[dt]['average'] = value_dict['value'] / value_dict['count']

        return_data = {
            'labels': [str(k) for k, v in calculated_days.items()],
            'values': [v['average'] for k, v in calculated_days.items()],
            'days': data['days'],
        }

    else:

        twx_oee = list(Smartkpivalues.objects.filter(kpidatetime__gte=range_from, kpidatetime__lt=range_to, kpiname='CVS: OEE (Version 2)', machine='KBLIBFP09-Lanico2MachineThing', kpitimebase='day').exclude(kpifloatvalue=0.0).values_list('kpidatetime', 'kpifloatvalue'))

        labels = [str(dt.date() + datetime.timedelta(days=1)) for (dt, value) in twx_oee]
        values = [value for (dt, value) in twx_oee]

        return_data = {
            'labels': list(labels),
            'values': list(values),
            'days': data['days'],
        }

    return JsonResponse(return_data)


@csrf_exempt
def fp09_alarm_descriptions(request):

    context = {
    }

    if request.method == "GET":
        if request.GET.get('reserves'):
            context.update({
                'descriptions': FP09_alarm_description.objects.all().order_by('code'),
                'reserves': True,
            })
        else:
            context.update({
                'descriptions': FP09_alarm_description.objects.exclude(description__icontains='Reserv').order_by('code')
            })

    if request.method == "POST":
        data = json.loads(request.body)

        if 'description' in data:
            FP09_alarm_description.objects.filter(id=data['alarm-id']).update(description=data['description'])
        if 'group' in data:
            FP09_alarm_description.objects.filter(id=data['alarm-id']).update(group=data['group'])
        if 'color' in data:
            FP09_alarm_description.objects.filter(id=data['alarm-id']).update(color_code=data['color'])

    return render(request, 'fp09_alarm_descriptions.html', context)


def fp09_stats(request):

    colors = list(FP09_alarm_description.objects.all().values('description', 'color_code'))
    group_colors = list(FP09_alarm_description.objects.all().values('group', 'color_code'))

    color_codes = {}

    for item in colors:
        color_codes[item['description']] = item['color_code']
        color_codes[item['description'][:25]] = item['color_code']

    for item in group_colors:
        color_codes[item['group']] = item['color_code']
        color_codes[item['group'][:25]] = item['color_code']

    return render(request, 'fp09_stats.html', context = {'colors': color_codes})


@csrf_exempt
def get_parts_count(request):

    data = json.loads(request.body)
    range_from = datetime.datetime.strptime(data['date'], "%Y-%m-%d")
    range_to = range_from + datetime.timedelta(days=1)

    description = data['label']

    if FP09_alarm_description.objects.filter(group=description).exists():
        codes = list(FP09_alarm_description.objects.filter(group=description).values_list('code', flat=True))
        parts_count = Tb_fp09_alarms.objects.filter(timestampalarm__gte=range_from, timestampalarm__lt=range_to, alarmcode__in=codes).values('alarmcode').aggregate(total=Count('alarmcode'))['total']
    else:
        code = FP09_alarm_description.objects.get(description=description).code
        parts_count = Tb_fp09_alarms.objects.filter(timestampalarm__gte=range_from, timestampalarm__lt=range_to, alarmcode=code).values('alarmcode').aggregate(total=Count('alarmcode'))['total']

    
    
    return JsonResponse({'resp' : parts_count})


@csrf_exempt
def fp09_data(request):

    data = json.loads(request.body)

    range_to = datetime.date.today()
    range_from = range_to - datetime.timedelta(days = data['days'])

    production_statistics = TbFp09Qd.objects.filter(productiontime__gte=range_from, productiontime__lte=range_to).filter(Q(formerstation="130") | (Q(formerstation="135") & Q(partstatus__in=["89", "105"]))).values('dsid', 'partstatus', 'productiontime', 'formerstation').annotate(day=Trunc('productiontime', 'day')).values('day').annotate(total_parts=Count('dsid')).order_by('day')

    total_production_in_period =  TbFp09Qd.objects.filter(productiontime__gte=range_from, productiontime__lte=range_to).filter(Q(formerstation="130") | (Q(formerstation="135") & Q(partstatus__in=["89", "105"]))).aggregate(total_parts=Count('dsid'))['total_parts']

    downtime_statistics = list(Tb_fp09_alarms.objects.filter(timestampalarm__gte=range_from, timestampalarm__lt=range_to).values('alarmcode').annotate(total=Count('alarmcode')).order_by('-total').values_list('alarmcode', 'total'))[:8]

    print(downtime_statistics)

    if data['type'] == 'group_pareto':

        results = {}

        groups = FP09_alarm_description.objects.all().values_list('group', flat=True).exclude(group='').distinct('group')

        for group in groups:
            group_alarm_codes = list(FP09_alarm_description.objects.filter(group=group).values_list('code', flat=True))
            results[group] = Tb_fp09_alarms.objects.filter(timestampalarm__gte=range_from, timestampalarm__lt=range_to, alarmcode__in=group_alarm_codes).aggregate(total=Count('alarmcode'))['total']

        downtime_ratio = [(key, value, value / total_production_in_period) for (key, value) in results.items()]

        downtime_ratio.sort(key = lambda tup: tup[2], reverse=True)

        return_data = {
            'days': data['days'],
            'data': downtime_ratio,
        }

    if data['type'] == 'pareto':

        downtime_ratio = [(FP09_alarm_description.objects.get(code=alarm_code).description, count, count / total_production_in_period ) for (alarm_code, count) in downtime_statistics]  

        return_data = {
            'days': data['days'],
            'data': downtime_ratio,
        }

    if data['type'] == 'line':

        alarm_reasons = [code for (code, total) in downtime_statistics]

        downtime_statistics_daily = list(Tb_fp09_alarms.objects.filter(timestampalarm__gte=range_from, timestampalarm__lt=range_to, alarmcode__in=alarm_reasons).annotate(day=Trunc('timestampalarm', 'day')).values('day', 'alarmcode').annotate(total=Count('alarmcode')).order_by('day', '-total').values_list('day', 'alarmcode', 'total'))
        print(range_from)
        print(range_to)


        days = []
        datasets = []

        daily_production = [item['total_parts'] for item in list(production_statistics)]

        for dict_data in list(production_statistics):
            days.append(dict_data['day'].date())
            
        for alarm_reason in alarm_reasons:
            dataset = {}
            dataset['label'] = FP09_alarm_description.objects.get(code=alarm_reason).description
            dataset['data'] = [(dt.date(), value) for (dt, code, value) in downtime_statistics_daily if (code == alarm_reason and dt.date() in days)]
            dataset['borderColor'] = 'rgb(255,255,255)'

            datasets.append(dataset)

            if len(days) > len(dataset['data']):
                days_in_alarms = (dt for (dt, value) in dataset['data'])
                missing_days = set(days) - set(days_in_alarms)
                for missing_day in missing_days:
                    dataset['data'].append((missing_day, 0))
                
                dataset['data'].sort(key = lambda tup: tup[0])


            dataset['data'] = [value for (dt, value) in dataset['data']]

            for idx, value in enumerate(dataset['data']):
                dataset['data'][idx] = value / daily_production[idx]

        return_data = {
            'days': data['days'],
            'days_in_range': days,
            'datasets': datasets,
            
        }


    if data['type'] == 'group_line':

        days = [] # v tyhle dny se vyrabelo, formate datetime.date
        daily_production = [item['total_parts'] for item in list(production_statistics)]

        for dict_data in list(production_statistics):
            days.append(dict_data['day'])

        datasets = []
        
        groups = FP09_alarm_description.objects.all().values_list('group', flat=True).exclude(group='').distinct('group')

        results = {}

        for group in groups:
            group_alarm_codes = list(FP09_alarm_description.objects.filter(group=group).values_list('code', flat=True))
            results[group] = list(Tb_fp09_alarms.objects.filter(timestampalarm__gte=range_from, timestampalarm__lt=range_to, alarmcode__in=group_alarm_codes).annotate(day=Trunc('timestampalarm', 'day')).order_by('day').values('day').annotate(total=Count('alarmcode')).values_list('day', 'total'))


            group_alarm_dates = [tup[0] for tup in results[group]]

            for day in days:
                if not day in group_alarm_dates:
                    results[group].append((day, 0))

            results[group].sort(key = lambda tup: tup[0])
            results[group] = [tup[1] for tup in results[group] if tup[0] in days]                

            for idx, value in enumerate(results[group]):
                results[group][idx] = (value / daily_production[idx], value)

        
        for group, values in results.items():
            dataset = {}
            dataset['label'] = group
            dataset['data'] = [tup[0] for tup in values]
            dataset['tooltips'] = [tup[1] for tup in values]
            dataset['borderColor'] = 'rgb(255,255,255)'
            datasets.append(dataset)


        return_data = {
            'days': data['days'],
            'days_in_range': [day.date() for day in days],
            'datasets': datasets,
            
        }
    
    return JsonResponse(return_data)


def local_infrastructure(request):

    infrastructure = Infrastructure.objects.all().order_by('id')

    return render(request, 'local_infrastructure.html', context = {'infrastructure': infrastructure})


@csrf_exempt
def ping_meskit(request):
    data = json.loads(request.body)
    meskit = Infrastructure.objects.get(meskit_ip=data['ip'])

    if data['force_offline'] == True:
        meskit.reboot_in_progress = False
        meskit.save()
        return JsonResponse(1, safe=False)
    
    result = os.system('ping -c 1 ' + data['ip'])

    if meskit.reboot_in_progress and result == 0:
        meskit.reboot_in_progress = False
        meskit.save()

    if meskit.reboot_in_progress and not result == 0:
        if meskit.last_restart < datetime.datetime.now() - datetime.timedelta(seconds=640):
            meskit.reboot_in_progress = False
            meskit.save()
            return JsonResponse(1, safe=False)

        return JsonResponse(999, safe=False)
    

    return JsonResponse(os.system('ping -c 1 ' + data['ip']), safe=False)


@csrf_exempt
def restart_meskit(request):

    data = json.loads(request.body)

    meskit = Infrastructure.objects.get(meskit_ip=data['ip'])

    session_id = '012345678901234567890123456789012'

    cookies = {
        'AIROS_SESSIONID': session_id,
    }   

    data = {
        'username': 'ubnt',
        'password': 'ubnt'
    }

    response = requests.post(f'http://{meskit.wifi_plug}/login.cgi', cookies=cookies, data=data)

    data = {
        'output': '0'
    }

    meskit.reboot_in_progress = True
    meskit.save()

    time.sleep(5)

    response = requests.put(f'http://{meskit.wifi_plug}/sensors/1', cookies=cookies, data=data)

    data = {
        'output': '1'
    }

    response = requests.put(f'http://{meskit.wifi_plug}/sensors/1', cookies=cookies, data=data)

    response = requests.get(f'http://{meskit.wifi_plug}/logout.cgi', cookies=cookies)


    return JsonResponse({'success': True, 'message': 'Testovaci zprava'})


@csrf_exempt
def reboot_meskit(request):

    data = json.loads(request.body)
    meskit = Infrastructure.objects.get(meskit_ip=data['ip'])
    meskit_ip = meskit.meskit_ip
    meskit_network_name = meskit.meskit_name

    if os.system('ping -c 1 ' + meskit_ip) != 0:
        return JsonResponse({'success': False, 'message': f"Meskit {meskit_network_name} není dostupný, zkuste tvrdý restart"})

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(meskit_ip, port=22, username='root', password='linux')

        time.sleep(5)

        stdin, stdout, stderr = ssh.exec_command('reboot')

        time.sleep(3)

        response_dict = {}
        response_dict['errors'] = []
        response_dict['output'] = []
        
        for line in stderr:
            response_dict['errors'].append(line)
        for line in stdout:
            response_dict['output'].append(line)

        meskit.reboot_in_progress = True
        meskit.save()    

        return JsonResponse({'success': True, 'message': f"Meskit {meskit_network_name} byl úspěšně restartován"})
    
    except:
        return JsonResponse({'success': False, 'message': f"Meskit {meskit_network_name} není dostupný, zkuste tvrdý restart"})
    
def dlp1_graph_test(request):
    context = {}
    return render(request, 'dlp1_graph_test.html', context)
    
def dlp1_screen(request):
    #Define variables
    machine = 'KBLIBFP08-Bayonet2MachineThing'
    now = datetime.datetime.now()
    now = datetime.datetime(2021,11,5,13,45,0)
    time = now.strftime('%H:%M')
    #Functions
    shift_start = shifts_start(now.strftime('%H'), now)
    #Get estimated DLP1 intervals
    last_partnumber, last_ordernumber, time_of_first_last_part = last_part(machine, now, shift_start)
    dlp1_estimated = dlp1_calculation(last_ordernumber, machine)
    coefficient_of_dlp1_in_timeintervals, actual_line_status, actual_line_status_time = get_time_intervals(time_of_first_last_part, now, machine)
    time_intervals, dlp1_estimated_intervals, time_intervals_in_hours_mins = get_dlp_estimated_intervals(coefficient_of_dlp1_in_timeintervals, dlp1_estimated)
    #Get real time DLP1 
    dlp1_real_time_intervals, total_production, rejects = get_dlp_real_time_intervals(time_intervals, last_ordernumber, time_of_first_last_part, now, machine)
    #Get monthly OEE
    monthly_OEE = get_monthly_OEE(machine, now)
    #Get monthly RQ
    monthly_RQ = get_monthly_RQ(machine, now)
    #Get number of workers
    operators, number_workers, time_workers = get_number_of_operators(machine, shift_start, now)
    #Edit DLP1 by workers
    dlp1_estimated_intervals = edit_dlp1_intervals_by_operators(dlp1_estimated_intervals, time_intervals, number_workers, time_workers, machine, shift_start, now)
    #DLP1 graph
    DLP1_average_shift_real, DLP1_average_shift_estimated = get_DLP1_graph(dlp1_real_time_intervals, dlp1_estimated_intervals)
    #OEE graph
    OEE_shift = get_OEE_graph(time_of_first_last_part, now, total_production, last_ordernumber, machine, dlp1_estimated)
    OEE_percent = round(OEE_shift*100,1)
    #RQ graph
    RQ_shift = round(total_production / (total_production + rejects), 3)
    RQ_percent = round(RQ_shift*100, 1)
    #Loss to one part - 15 min
    loss_to_one_part, time_intervals_loss = get_loss_to_one_part(dlp1_real_time_intervals, dlp1_estimated_intervals, time_intervals_in_hours_mins)
    #Get number of estimated total production
    estimated_total_production = sum(dlp1_estimated_intervals) / 4
    #Get top 5 line defects
    top_5_line_defects, top_5_line_defects_count, line_defects_percent, organization_loss_percent = get_top_5_line_defects(machine, shift_start, now)
    #Get top 5 NOK defects
    top_5_NOK_defects, top_5_NOK_defects_count, rejects_shift = get_top_5_NOK_defects(machine, shift_start, now)
    #Get total production - order
    total_production_order, time_of_first_part_in_order = get_total_production_order(last_ordernumber, machine, now)
    coefficient_order, actual_line_status2, actual_line_status_time = get_time_intervals(time_of_first_part_in_order, now, machine)
    operators_order, number_workers_order, time_workers_order = get_number_of_operators(machine, time_of_first_part_in_order - datetime.timedelta(hours=8), now)
    dlp1_estimated_intervals_without_workers, time_intervals_order = get_dlp1_estimated_intervals_without_workers(coefficient_order, dlp1_estimated)
    dlp1_estimated_intervals_order = edit_dlp1_intervals_by_operators(dlp1_estimated_intervals_without_workers, time_intervals_order, number_workers_order, time_workers, machine, time_of_first_part_in_order, now) 
    total_production_order_estimated = get_total_production_order_estimated(dlp1_estimated_intervals_order)
    #Translate top 5 line defects
    top_5_line_defects_translated = translate_top_5_line_defects(top_5_line_defects, machine)
    #Translate top 5 NOK defects
    top_5_NOK_defects_translated = translate_top_5_NOK_defects(top_5_NOK_defects, machine)
    #Translate actual status
    actual_line_status_translated = translate_actual_line_status(actual_line_status, machine)
    #Get Order Scheduled Start, Finish, Processing Time
    Processing_time_order = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber = last_ordernumber, propertykey1 = "ProcessingTimeAPO").values_list('floatvalue','textvalue'))
    Scheduled_start_order = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber = last_ordernumber, propertykey1 = "EarliestScheduledStartExecution").values_list('datetimevalue', 'ordernumber'))
    Scheduled_end_order = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber = last_ordernumber, propertykey1 = "EarliestScheduledFinishExecution").values_list('datetimevalue', 'ordernumber'))
    #Get SAP APO
    Estimated_total_shift_production_sap_apo = get_estimated_total_shift_production_sap_apo(shift_start, now, machine, Processing_time_order, time_of_first_last_part)
    Estimated_total_order_production_sap_apo = get_estimated_total_order_production_sap_apo(Scheduled_start_order[0][0], Scheduled_end_order[0][0], now, machine, Processing_time_order)
    #Find Shift Fabricated parts + Processing time
    Production_times_and_losses, total_parts_in_dict = get_production_time_and_loses(line_defects_percent, organization_loss_percent, shift_start, now, machine)
    #Get Target of Order
    Target_order = get_target_order(Scheduled_start_order[0][0], Scheduled_end_order[0][0], time_of_first_last_part, Processing_time_order, machine, shift_start)
    Target_order_full = get_target_order_full(Scheduled_start_order[0][0], Scheduled_end_order[0][0], Processing_time_order, machine)
    #Get total shift production
    print(total_parts_in_dict, last_ordernumber)
    Total_shift_production_actual = sum(total_parts_in_dict.values())
    Total_shift_production_estimated = get_estimated_shift_production(machine, total_parts_in_dict, shift_start, now, last_ordernumber, Processing_time_order)
    
    for key in total_parts_in_dict:
        if key == last_ordernumber:
            actual_total_order_production_in_shift = total_parts_in_dict[key]

    context = {'dlp1_real_time_intervals': dlp1_real_time_intervals,
                'dlp1_estimated_intervals': dlp1_estimated_intervals,
                'time_intervals': time_intervals_in_hours_mins,
                'last_partnumber': last_partnumber,
                'last_ordernumber': last_ordernumber,
                'monthly_OEE': monthly_OEE,
                'monthly_RQ': monthly_RQ,
                'operators': operators,
                'DLP1_average_shift_real': DLP1_average_shift_real,
                'DLP1_average_shift_estimated': DLP1_average_shift_estimated,
                'OEE_shift': OEE_percent,
                'RQ_shift': RQ_percent,
                'loss_to_one_part': loss_to_one_part,
                'estimated_total_production': estimated_total_production,
                'actual_line_status': actual_line_status_translated,
                'actual_line_status_time': actual_line_status_time,
                'top_5_line_defects': top_5_line_defects_translated,
                'top_5_line_defects_count': top_5_line_defects_count,
                'top_5_NOK_defects': top_5_NOK_defects_translated,
                'top_5_NOK_defects_count': top_5_NOK_defects_count,
                'total_production': total_production,
                'machine': machine,
                'time': time,
                'line_defects_percent': line_defects_percent,
                'rejects_last_part': rejects,
                'rejects': rejects_shift,
                'total_production_order': total_production_order,
                'total_production_order_estimated': total_production_order_estimated,
                'Estimated_total_shift_production_sap_apo': round(Estimated_total_shift_production_sap_apo, 0),
                'Estimated_total_order_production_sap_apo': round(Estimated_total_order_production_sap_apo, 0),
                'Production_times_and_losses': Production_times_and_losses,
                'Target_order': Target_order,
                'Target_order_full': Target_order_full,
                'Total_shift_production_actual': Total_shift_production_actual,
                'Total_shift_production_estimated': Total_shift_production_estimated,
                'actual_total_order_production_in_shift': actual_total_order_production_in_shift,
                'time_intervals_loss': time_intervals_loss
    }
  

    return render(request, 'dlp1_2.html', context)

def dlp1_screen_operator(request):
    #Define variables
    machine = 'KBLIBFP08-Bayonet2MachineThing'
    now = datetime.datetime.now()
    now = datetime.datetime(2021,11,5,13,45,0)
    time = now.strftime('%H:%M')
    #Functions
    shift_start = shifts_start(now.strftime('%H'), now)
    #Get estimated DLP1 intervals
    last_partnumber, last_ordernumber, time_of_first_last_part = last_part(machine, now, shift_start)
    dlp1_estimated = dlp1_calculation(last_ordernumber, machine)
    coefficient_of_dlp1_in_timeintervals, actual_line_status, actual_line_status_time = get_time_intervals(time_of_first_last_part, now, machine)
    time_intervals, dlp1_estimated_intervals, time_intervals_in_hours_mins = get_dlp_estimated_intervals(coefficient_of_dlp1_in_timeintervals, dlp1_estimated)
    #Get real time DLP1 
    dlp1_real_time_intervals, total_production, rejects = get_dlp_real_time_intervals(time_intervals, last_ordernumber, time_of_first_last_part, now, machine)
    #Get monthly OEE
    monthly_OEE = get_monthly_OEE(machine, now)
    #Get monthly RQ
    monthly_RQ = get_monthly_RQ(machine, now)
    #Get number of workers
    operators, number_workers, time_workers = get_number_of_operators(machine, shift_start, now)
    #Edit DLP1 by workers
    dlp1_estimated_intervals = edit_dlp1_intervals_by_operators(dlp1_estimated_intervals, time_intervals, number_workers, time_workers, machine, shift_start, now)
    #Get top 5 line defects
    top_5_line_defects, top_5_line_defects_count, line_defects_percent, organization_loss_percent = get_top_5_line_defects(machine, shift_start, now)
    #Get total production - order
    total_production_order, time_of_first_part_in_order = get_total_production_order(last_ordernumber, machine, now)
    coefficient_order, actual_line_status2, actual_line_status_time = get_time_intervals(time_of_first_part_in_order, now, machine)
    operators_order, number_workers_order, time_workers_order = get_number_of_operators(machine, time_of_first_part_in_order - datetime.timedelta(hours=8), now)
    dlp1_estimated_intervals_without_workers, time_intervals_order = get_dlp1_estimated_intervals_without_workers(coefficient_order, dlp1_estimated)
    dlp1_estimated_intervals_order = edit_dlp1_intervals_by_operators(dlp1_estimated_intervals_without_workers, time_intervals_order, number_workers_order, time_workers, machine, time_of_first_part_in_order, now) 
    total_production_order_estimated = get_total_production_order_estimated(dlp1_estimated_intervals_order)
    #Translate actual status
    actual_line_status_translated = translate_actual_line_status(actual_line_status, machine)
    #Get Order Scheduled Start, Finish, Processing Time
    Processing_time_order = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber = last_ordernumber, propertykey1 = "ProcessingTimeAPO").values_list('floatvalue','textvalue'))
    Scheduled_start_order = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber = last_ordernumber, propertykey1 = "EarliestScheduledStartExecution").values_list('datetimevalue', 'ordernumber'))
    Scheduled_end_order = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber = last_ordernumber, propertykey1 = "EarliestScheduledFinishExecution").values_list('datetimevalue', 'ordernumber'))
    #Get SAP APO
    Estimated_total_shift_production_sap_apo = get_estimated_total_shift_production_sap_apo(shift_start, now, machine, Processing_time_order, time_of_first_last_part)
    Estimated_total_order_production_sap_apo = get_estimated_total_order_production_sap_apo(Scheduled_start_order[0][0], Scheduled_end_order[0][0], now, machine, Processing_time_order)
    #Find Shift Fabricated parts + Processing time
    Production_times_and_losses, total_parts_in_dict = get_production_time_and_loses(line_defects_percent, organization_loss_percent, shift_start, now, machine)
    #Get Target of Order
    Target_order = get_target_order(Scheduled_start_order[0][0], Scheduled_end_order[0][0], time_of_first_last_part, Processing_time_order, machine, shift_start)
    Target_order_full = get_target_order_full(Scheduled_start_order[0][0], Scheduled_end_order[0][0], Processing_time_order, machine)
    #Get total shift production
    print(total_parts_in_dict, last_ordernumber)
    Total_shift_production_actual = sum(total_parts_in_dict.values())
    Total_shift_production_estimated = get_estimated_shift_production(machine, total_parts_in_dict, shift_start, now, last_ordernumber, Processing_time_order)
    
    for key in total_parts_in_dict:
        if key == last_ordernumber:
            actual_total_order_production_in_shift = total_parts_in_dict[key]

    context = { 'last_partnumber': last_partnumber,
                'last_ordernumber': last_ordernumber,
                'monthly_OEE': monthly_OEE,
                'monthly_RQ': monthly_RQ,
                'operators': operators,
                'actual_line_status': actual_line_status_translated,
                'total_production': total_production,
                'machine': machine,
                'time': time,
                'total_production_order': total_production_order,
                'total_production_order_estimated': total_production_order_estimated,
                'Estimated_total_shift_production_sap_apo': round(Estimated_total_shift_production_sap_apo, 0),
                'Estimated_total_order_production_sap_apo': round(Estimated_total_order_production_sap_apo, 0),
                'Target_order': Target_order,
                'Target_order_full': Target_order_full,
                'Total_shift_production_actual': Total_shift_production_actual,
                'Total_shift_production_estimated': Total_shift_production_estimated,
                'actual_total_order_production_in_shift': actual_total_order_production_in_shift,
    }
    return render(request, 'dlp1_operator.html', context)

def times_comparison(request):
    machines_all = list(MachinesConverter.objects.values_list('machine_name', flat=True).distinct())
    machines_ordernumbers_dict = {}
    for machine in machines_all:
        ordernumber_last = Smartkpi.objects.filter(machine = machine).exclude(ordernumber__in = ['dummy_no', 'Kalibrace', 'dummy_ok']).values_list('ordernumber', flat=True).last()
        machines_ordernumbers_dict[machine] = ordernumber_last
        dlp1, total_parts = get_dlp1_of_last_ordernumber(machine, ordernumber_last)
        apo_time = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber = ordernumber_last, propertykey1 = "ProcessingTimeAPO").values_list('floatvalue','textvalue'))
        if apo_time[0][1] == 'MIN':
            apo_time_in_sec = round(apo_time[0][0] * 60,2)
        elif apo_time[0][1] == 'SEC':
            apo_time_in_sec = round(apo_time[0][0])
        machines_ordernumbers_dict[machine] = []
        machines_ordernumbers_dict[machine].append(ordernumber_last)
        machines_ordernumbers_dict[machine].append(dlp1)
        if dlp1 == '-':
            machines_ordernumbers_dict[machine].append('-')
            machines_ordernumbers_dict[machine].append(apo_time_in_sec)
            machines_ordernumbers_dict[machine].append('-')
            machines_ordernumbers_dict[machine].append('-')
            machines_ordernumbers_dict[machine].append('-')
        else:
            machines_ordernumbers_dict[machine].append(round(3600/dlp1,2))
            machines_ordernumbers_dict[machine].append(apo_time_in_sec)
            machines_ordernumbers_dict[machine].append(round(3600/dlp1 - apo_time_in_sec, 2))
            machines_ordernumbers_dict[machine].append(round((3600/dlp1 - apo_time_in_sec)/(3600/dlp1) * 100,2))
            machines_ordernumbers_dict[machine].append(total_parts)
    context = {
        'machines_ordernumbers_dict': machines_ordernumbers_dict,
    }
    return render(request, 'times_comparison.html', context)

def plant_view(request):

    machines_all = list(Smartkpi.objects.exclude(machine__contains="Station").values_list('machine').distinct())
    machines_active = list(Smartkpi.objects.filter(creationtime__gte='2020-07-13').exclude(machine__contains="Station").values_list('machine').distinct())
    machines_inactive = list(set(machines_all) - set(machines_active))

    context = {
        'machines': machines_all,
        'machines_active': machines_active,
        'machines_inactive': machines_inactive,
    }

    return render(request, 'plant_view.html', context)


def machine_view(request):

    data = Smartkpi.objects.filter(machine=request.GET.get('machine'), creationtime__gte='2020-07-13 13:30')

    for i in range(len(data)):
        try:
            partnumber_object = PartNumber.objects.get(partnumber=data[i].partnumber)
            data[i].sapapotime = partnumber_object.sapapotime
        except:
            pass
        finally:
            if i > 0:
                data[i].production_time = (data[i].creationtime - data[i-1].creationtime).total_seconds()
            else:
                data[i].production_time = 'First in series'

    context = {
        'data': data,
    }

    return render(request, 'machine_view.html', context)


def partno_view(request):

    if request.method == "POST":

        filters = {}
        
        if request.POST.get('date_from'):
            filters['productiontime__gte'] = datetime.datetime.fromisoformat(request.POST.get('date_from')).replace(tzinfo=None)
        else:
            filters['productiontime__gte'] = datetime.datetime.now() - datetime.timedelta(days=30)

        if request.POST.get('date_to'):
            raw_date = datetime.datetime.fromisoformat(request.POST.get('date_to')).replace(tzinfo=None)
            filters['productiontime__lte'] = raw_date
        else:
            filters['productiontime__lte'] = datetime.datetime.now()

        partnos = Smartkpi.objects.filter(productiontime__gte='2020-01-01').values('partnumber', 'machine').exclude(machine__icontains='StationThing').distinct().order_by('partnumber')
        data = Smartkpi.objects.filter(partnumber=request.POST.get('partno').split(" ")[0]).filter(machine=str('KBLIB') + str(request.POST.get('partno').split(" ")[1]) + 'MachineThing').filter(**filters).exclude(machine__icontains='StationThing').order_by('productiontime')

        if data.count() > 0:

            line_x = []
            line_y = []

            for i in range(len(data)):
                if i > 0:
                    data[i].production_time = (data[i].productiontime - data[i-1].productiontime).total_seconds()
                    line_y.append(data[i].production_time)
                    line_x.append(str(data[i].productiontime))
                else:
                    data[i].production_time = 0

            temp_list = list(zip(line_x, line_y))
            temp_list_2 = [(item[0], item[1]) for item in temp_list]

            line_x = []
            line_y = []

            for item in temp_list_2:
                line_x.append(item[0])
                line_y.append(item[1])

            count = len(line_y)
            mean = sum(line_y) / len(line_y)
            median = statistics.median(line_y)

            temp_list_reduced = [(item[0], item[1]) for item in temp_list if not item[1] > 10 * median]
        
            line_x = []
            line_y = []
            viol_x = []
            viol_y = []

            order_number = Smartkpiorderkeyvaluedata.objects.filter(textvalue=request.POST.get('partno').split(" ")[0]).values_list('ordernumber', flat=True).last()

            sapapotime_twx = Smartkpiorderkeyvaluedata.objects.filter(ordernumber=order_number, propertykey='ProcessingTimeAPO-0010').values_list('floatvalue', 'textvalue').last()

            if sapapotime_twx == None:
                sapapotime_twx = Smartkpiorderkeyvaluedata.objects.filter(ordernumber=order_number, propertykey='ProcessingTimeAPO-0020').values_list('floatvalue', 'textvalue').last()


            tgmax_twx = Smartkpiorderkeyvaluedata.objects.filter(ordernumber=order_number, propertykey='tgMaxTime-0010').values_list('floatvalue', 'textvalue').last()

            try:
                if sapapotime_twx[1] == 'MIN':
                    object_sapapotime_twx = sapapotime_twx[0] * 60
                else:
                    object_sapapotime_twx = sapapotime_twx[0]
            except:
                object_sapapotime_twx = 0

            try:
                if tgmax_twx[1] == 'MIN':
                    object_tgmax_twx = tgmax_twx[0] * 60
                else:
                    object_tgmax_twx = tgmax_twx[0]
            except:
                object_tgmax_twx = 0


            for item in temp_list_reduced:
                line_x.append(item[0])
                line_y.append(item[1])
                if item[1] > object_sapapotime_twx:
                    viol_x.append(item[0])
                    viol_y.append(item[1])

            lcl_x = []
            lcl_y = []
            lcl_x.append(min(line_x))
            lcl_x.append(max(line_x))
            lcl_y.append(object_sapapotime_twx)
            lcl_y.append(object_sapapotime_twx)
            mean_x = []
            mean_y = []
            mean_x.append(min(line_x))
            mean_x.append(max(line_x))

            count = len(line_y)
            mean = sum(line_y) / len(line_y)
            median = statistics.median(line_y)

            try:
                standard_deviation = statistics.stdev(line_y)
            except:
                standard_deviation = 0

            outliers = 0

            mean_y.append(mean)
            mean_y.append(mean)

            for item in line_y:
                if item > (10 * median):
                    outliers += 1

            context = {
                'partnos': partnos,
                'partno': request.POST.get('partno'),
                'data': data,
                'line_x': line_x,
                'line_y': line_y,
                'viol_x': viol_x,
                'viol_y': viol_y,
                'lcl_x': lcl_x,
                'lcl_y': lcl_y,
                'mean_x': mean_x,
                'mean_y': mean_y,
                'median': median,
                'standard_deviation': standard_deviation,
                'mean': mean,
                'count': count,
                'outliers_count': outliers,
                'outliers_percentage': (outliers / count) * 100,
            }

            if request.POST.get('date_from'):
                context.update(
                    {'date_from': request.POST.get('date_from')}
                )
            else:
                context.update(
                    {'date_90': datetime.datetime.now() - datetime.timedelta(days=90)}
                )

            if request.POST.get('date_to'):
                context.update(
                    {'date_to': request.POST.get('date_to')}
                )
            else:
                context.update(
                    {'date_today': datetime.datetime.now()}
                )

            context.update(
                {'sap_apo_time': object_sapapotime_twx, 'sap_tgmax_time': object_tgmax_twx},
            )
    
        else:
            context = {
                'partnos': partnos,
                'message': "Not found",
                'partno': request.POST.get('partno'),
            }

            if request.POST.get('date_from'):
                context.update(
                    {'date_from': request.POST.get('date_from')}
                )
            else:
                context.update(
                    {'date-90': datetime.datetime.now() - datetime.timedelta(days=90)}
                )

            if request.POST.get('date_to'):
                context.update(
                    {'date_to': request.POST.get('date_to')}
                )
            else:
                context.update(
                    {'date-today': datetime.datetime.now()}
                )

        return render(request, 'partno_view.html', context)


    if request.method == "GET":
        
        partnos = Smartkpi.objects.filter(productiontime__gte='2020-01-01').exclude(machine__icontains='StationThing').exclude(partnumber='').values('partnumber', 'machine').distinct().order_by('partnumber')
        
        context = {
            'partnos': partnos,
            'date_90': datetime.datetime.now() - datetime.timedelta(days=90),
            'date_today': datetime.datetime.now(),
        }

    return render(request, 'partno_view.html', context)



def show_smartkpiorderkeyvaluedata(request):

    objects = Smartkpiorderkeyvaluedata.objects.filter(creationtime__gte='2020-08-18')

    context = {
        'objects': objects
    }

    return render(request, 'smartkpiorderkeyvaluedata.html', context)


def show_smartkpimachinemessagedata(request):

    objects = Smartkpimachinemessagedata.objects.filter(creationtime__gte='2020-08-19', machine='KBLIBFP08-Bayonet2PromoticStationThing').exclude(description='Automatic Input')
    
    context = {
        'objects': objects
    }

    return render(request, 'smartkpimachinemessagedata.html', context)


def show_smartkpi(request):

    objects = Smartkpi.objects.filter(creationtime__gte='2020-08-18 06:00:00', creationtime__lte='2020-08-18 13:59:59', machine='KBLIBFP08-Bayonet2MachineThing')
    last_object_shift_before = Smartkpi.objects.filter(creationtime__lte='2020-08-18 06:00:00', machine='KBLIBFP08-Bayonet2MachineThing').last()

    production = {}


    for obj in objects:
        if not obj.machine in production:
            production[obj.machine] = {}
            production[obj.machine][obj.partnumber] = {}
            production[obj.machine][obj.partnumber]['pcs'] = 1
            production[obj.machine][obj.partnumber]['apo_time'] = getTime(obj.partnumber, machine=obj.machine)
            production[obj.machine][obj.partnumber]['average_production_time'] = getProductionTimeAverage(obj.partnumber, '2020-08-18 06:00:00', '2020-08-18 13:59:59')[0]
        else:
            if not obj.partnumber in production[obj.machine]:
                production[obj.machine][obj.partnumber] = {}
                production[obj.machine][obj.partnumber]['pcs'] = 1
                production[obj.machine][obj.partnumber]['apo_time'] = getTime(obj.partnumber, machine=obj.machine)
                production[obj.machine][obj.partnumber]['average_production_time'] = getProductionTimeAverage(obj.partnumber, '2020-08-18 06:00:00', '2020-08-18 13:59:59')[0]
            else:
                production[obj.machine][obj.partnumber]['pcs'] += 1
    
    for machine, data in production.items():
        for partnumber, values in data.items():
            production[machine][partnumber]['total_apo_time_hours'] = (production[machine][partnumber]['pcs'] * production[machine][partnumber]['apo_time']) / 3600
            production[machine][partnumber]['total_production_time_hours'] = (production[machine][partnumber]['pcs'] * production[machine][partnumber]['average_production_time']) / 3600

    context = {
        'objects': objects,
        'production': production,
    }

    return render(request, 'smartkpi.html', context)


def getTgmaxTime(partnumber, **kwargs):

    try:
        if 'machine' in kwargs:
            machine = kwargs['machine']
            machine = machine.replace('MachineThing', '')
            ordernumbers = list(Smartkpiorderkeyvaluedata.objects.filter(propertykey='MaterialNumber', textvalue=partnumber).values_list('ordernumber', flat=True))
            machine_specific_order_number = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=ordernumbers).filter(textvalue__icontains=machine[-5:]).values_list('ordernumber', flat=True))[-1]

            tgmax = Smartkpiorderkeyvaluedata.objects.filter(propertykey='tgMaxTime-0010', ordernumber=machine_specific_order_number).values_list('floatvalue', 'textvalue').last()
        else:
            ordernumber = list(Smartkpiorderkeyvaluedata.objects.filter(propertykey='MaterialNumber', textvalue=partnumber).values_list('ordernumber', flat=True))[-1]

            tgmax = Smartkpiorderkeyvaluedata.objects.filter(propertykey='tgMaxTime-0010', ordernumber=ordernumber).values_list('floatvalue', 'textvalue').last()

        if tgmax[1] == "MIN":
            return tgmax[0] * 60
        else:
            return tgmax[0]

    except:
        return 0


def getTime(partnumber, *dates, **kwargs):

    try:
        if 'machine' in kwargs:
            machine = kwargs['machine']
            machine = machine.replace('MachineThing', '')
            order_number = list(Smartkpiorderkeyvaluedata.objects.filter(propertykey='MaterialNumber', textvalue=partnumber).values_list('ordernumber', flat=True))
            machine_specific_order_number = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=order_number).filter(textvalue__icontains=machine[-5:]).values_list('ordernumber', flat=True))[-1]
            time = Smartkpiorderkeyvaluedata.objects.filter(ordernumber=machine_specific_order_number, propertykey__startswith='ProcessingTimeAPO').values_list('floatvalue', 'textvalue').last()
        else:
            order_number = list(Smartkpiorderkeyvaluedata.objects.filter(propertykey='MaterialNumber', textvalue=partnumber).values_list('ordernumber', flat=True))[-1]
            time = Smartkpiorderkeyvaluedata.objects.filter(ordernumber=order_number, propertykey__startswith='ProcessingTimeAPO').values_list('floatvalue', 'textvalue').last()

        if time[1] == 'MIN':
            return time[0] * 60
        else:
            return time[0]  

    except:
        return 0


def mass_ofset(request):

    context = {}

    if request.method == "GET":
        date_from = datetime.datetime.now() - datetime.timedelta(hours=8)
        date_to = datetime.datetime.now()

    if request.method == "POST":
        machines_to_input = []
        filters = {}

        date_from = datetime.datetime.fromisoformat(request.POST.get('date_from'))
        date_to = datetime.datetime.fromisoformat(request.POST.get('date_to'))

        if request.POST.get('machines'):
            machines = request.POST.getlist('machines')

            denormalized_machines = []

            for machine in machines:
                denormalized_machines.append('KBLIB' + machine + 'MachineThing')
                machines_to_input.append(machine)
        
        if not 'machines' in request.POST:
            machines = list(Smartkpi.objects.filter(creationtime__gte='2020-09-01').values_list('machine', flat=True).exclude(machine__icontains='StationThing').distinct())
        
            denormalized_machines = []

            for machine in machines:
                denormalized_machines.append(machine)
                machines_to_input.append(machine)

        filters['machine__in'] = denormalized_machines

        context.update({
            'selected_machines': denormalized_machines,
            'machines_to_input': machines_to_input,
        })

        filters['productiontime__gte'] = date_from
        filters['productiontime__lte'] = date_to

        all_partnos = list(Smartkpi.objects.filter(**filters).exclude(machine__icontains='StationThing').values_list('partnumber', 'machine').order_by('machine').distinct())

    context.update({
        'date_from': date_from,
        'date_to': date_to,
        'machines': Smartkpi.objects.filter(creationtime__gte='2020-09-01').values_list('machine', flat=True).exclude(machine__icontains='StationThing').distinct(),
    })

    if request.method == "POST":
        ofset = {}
    
        for partno in all_partnos:
            if not partno == '':
                ofset[partno] = {}
                if 'OC18' in partno[1]:
                    ofset[partno]['apo'] = getTime(partno[0], date_from, date_to, machine=partno[1])
                else:
                    ofset[partno]['apo'] = getTime(partno[0], date_from, date_to)
                ofset[partno]['average'], ofset[partno]['count'], ofset[partno]['median'] = getProductionTimeAverage(partno[0], date_from, date_to, machine=partno[1])
                ofset[partno]['apo_vs_average'] = ofset[partno]['apo'] - ofset[partno]['average']
                if 'OC18' in partno[1]:
                    ofset[partno]['tgmax'] = getTgmaxTime(partno[0], machine=partno[1])
                else:
                    ofset[partno]['tgmax'] = getTgmaxTime(partno[0])
                ofset[partno]['tgmax_vs_median'] = ofset[partno]['tgmax'] - ofset[partno]['median'] 
                ofset[partno]['machine'] = partno[1]
                try:
                    ofset[partno]['production_group'] = ProductionGroup.objects.get(machine=partno[1], material_number=partno[0]).values_list('production_group', flat=True)[0]
                except:
                    try:
                        ofset[partno]['production_group'] = ProductionGroup.objects.filter(material_number=partno[0]).first().production_group
                    except:
                        ofset[partno]['production_group'] = 'NA'

                try:
                    ofset[partno]['effort'] = PartNumberEffort.objects.get(partnumber=partno[0], machine=partno[1]).effort
                except:
                    try:
                        ofset[partno]['effort'] = StandardLineOccupancy.objects.get(machine=ofset[partno]['machine']).occupancy * (ofset[partno]['tgmax'] - (StandardLineOccupancy.objects.get(machine=ofset[partno]['machine']).waste * ofset[partno]['tgmax']))
                    except:
                        ofset[partno]['effort'] = 0
                        
                try:
                    ofset[partno]['operators'] = ofset[partno]['effort'] / ofset[partno]['median']
                except:
                    ofset[partno]['operators'] = 1

                if ofset[partno]['operators'] - truncate(ofset[partno]['operators']) < 0.2:
                    # ofset[partno]['operators'] = math.floor(ofset[partno]['operators'])
                    ofset[partno]['operators'] = ofset[partno]['operators']
                else:
                    # ofset[partno]['operators'] = math.ceil(ofset[partno]['operators'])
                    ofset[partno]['operators'] = ofset[partno]['operators']



        context.update({
            'ofset': ofset,
        })

    return render(request, 'mass.html', context)
    

def getProductionTimeAverage(partnumber, *dates, machine):

    all_objs = Smartkpi.objects.filter(partnumber=partnumber, productiontime__gte=dates[0], productiontime__lte=dates[1], machine=machine).exclude(machine__icontains='StationThing').order_by('productiontime')

    production_times = []

    for i in range(len(all_objs)):
        if i > 0:
            all_objs[i].production_time = (all_objs[i].productiontime - all_objs[i-1].productiontime).total_seconds()
        else:
            all_objs[i].production_time = 0

        production_times.append(all_objs[i].production_time)

    try:
        median = statistics.median(production_times)
    except:
        try:
            median = sum(production_times)/len(production_times)
        except:
            median = 0

    production_times_2 = [i for i in production_times if not i > 10 * median]

    try:
        new_median = statistics.median(production_times_2)
    except:
        new_median = 0

    try:
        average = sum(production_times_2)/len(production_times_2)
    except:
        average = 0

    return [average, len(production_times_2), new_median]

@csrf_exempt
def get_tgmax(request, ordernumber = None):

    if not ordernumber:
        ordernumber = json.loads(request.POST.get('order'))

        tgmax_times = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber=ordernumber, propertykey1='tgMaxTime').values_list('propertykey', flat=True))

        tgmax = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber=ordernumber, propertykey__in=tgmax_times).values_list('floatvalue', 'textvalue'))

        tgmax_total = 0

        for tup in tgmax:
            if tup[1] == "MIN":
                tgmax_total += tup[0]*60
            else:
                tgmax_total += tgmax[0]

        return HttpResponse(str(round(tgmax_total, 2)))

    else:
        tgmax_times = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber=ordernumber, propertykey1='tgMaxTime').values_list('propertykey', flat=True))

        tgmax = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber=ordernumber, propertykey__in=tgmax_times).values_list('floatvalue', 'textvalue'))

        tgmax_total = 0

        for tup in tgmax:
            if tup[1] == "MIN":
                tgmax_total += tup[0]*60
            else:
                tgmax_total += tup[0]

        return round(tgmax_total, 2)


@csrf_exempt
def get_tgmax_group(request):

    raw_ordernumbers = request.POST.get('orders')

    ordernumbers = raw_ordernumbers.split("|")

    tuples = [(ordernumbers[i], ordernumbers[i+1]) for i in range(0, len(ordernumbers), 2)]

    plain_order_numbers = set()
    plain_operations = set()
    operations_text = []

    for i in range(0, len(ordernumbers)):
        if i % 2:
            plain_operations.add(ordernumbers[i])
        else:
            plain_order_numbers.add(ordernumbers[i])
    
    for operation_number in plain_operations:
        operations_text.append('tgMaxTime-' + operation_number)

    tgmaxs = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=plain_order_numbers, propertykey__in=operations_text).values_list('floatvalue', 'textvalue', 'ordernumber', 'propertykey'))

    tgmaxs_order_operations_only = set(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=plain_order_numbers, propertykey__in=operations_text).values_list('ordernumber', 'propertykey'))

    tgmaxs_order_operations_only_adjusted = [(tup[0], tup[1][-4:]) for tup in tgmaxs_order_operations_only]

    tgmaxs_order_operations_only_adjusted_2 = [item for item in tgmaxs_order_operations_only_adjusted if item in tuples]

    diff = list(set(tgmaxs_order_operations_only_adjusted) - set(tgmaxs_order_operations_only_adjusted_2))

    if diff:
        for item in tgmaxs:
            if item[2] == diff[0][0] and item[3][-4:] == diff[0][1]:
                tgmaxs.remove(item)

    missing_order_operation_combination = set(tuples) - set(tgmaxs_order_operations_only_adjusted_2)

    values_list = [(tgmaxtuple[0], str(tgmaxtuple[2]), str(tgmaxtuple[3])) if tgmaxtuple[1] == "SEC" else ((tgmaxtuple[0] * 60), str(tgmaxtuple[2]), str(tgmaxtuple[3])) for tgmaxtuple in tgmaxs]

    missing_order_operation_combination_with_0 = [(0, tup[0], tup[1]) for tup in missing_order_operation_combination]

    for trituple in missing_order_operation_combination_with_0:
        values_list.append(trituple)

    sorted_values_list = sorted(values_list, key=itemgetter(1,2))

    new_values_list = [str(tup[0]) for tup in sorted_values_list]

    return_string = '|'.join(new_values_list)

    return HttpResponse(return_string)



def get_apo(request):
    return None


@csrf_exempt
def get_oee(request):
    context = {}

    lines_with_aliases = [('KBLIBADBMachineThing', 'ADB'), ('KBLIBAoHMachineThing', 'AoH'), ('KBLIBBSMachineThing', 'BS'), ('KBLIBDMC80H-OC18AMachineThing', 'DMC80H-OC18A'), ('KBLIBDMC80H-OC18BMachineThing', 'DMC80H-OC18B'), ('KBLIBDMC80H-OC18CMachineThing', 'DMC80H-OC18C'), ('KBLIBDMC80H-OC18DMachineThing', 'DMC80H-OC18D'), ('KBLIBDMC80H-OC18EMachineThing', 'DMC80H-OC18E'), ('KBLIBDMC80H-OC18FMachineThing', 'DMC80H-OC18F'), ('KBLIBDMC80H-OC18GMachineThing', 'DMC80H-OC18G'), ('KBLIBDMC80H-OC18HMachineThing', 'DMC80H-OC18H'), ('KBLIBDMC80H-OC18IMachineThing', 'DMC80H-OC18I'), ('KBLIBDMC80H-OC18JMachineThing', 'DMC80H-OC18J'), ('KBLIBDMC80H-OC18KMachineThing', 'DMC80H-OC18K'), ('KBLIBDMC80H-OC19AMachineThing', 'DMC80H-OC19A'), ('KBLIBDPAMachineThing', 'DPA'), ('KBLIBFP08-Bayonet2MachineThing', 'FP08-Bayonet2'), ('KBLIBFP09-Lanico2MachineThing', 'FP09-Lanico2'), ('KBLIBFP1_2MachineThing', 'FP1_2'), ('KBLIBFP-BayonetMachineThing', 'FP-Bayonet'), ('KBLIBFP-LanicoMachineThing', 'FP-Lanico'), ('KBLIBKBEMachineThing', 'KBE'), ('KBLIBMCMachineThing', 'MC'), ('KBLIBNG4MachineThing', 'NG4'), ('KBLIBOBC-1MachineThing', 'OBC-1'), ('KBLIBOBC-2MachineThing', 'OBC-2'), ('KBLIBOBC-3MachineThing', 'OBC-3'), ('KBLIBSMMachineThing', 'SM'), ('KBLIBVGMachineThing', 'VG'), ('KBLIBWedgeMachineThing', 'Wedge')]

    context.update({
        'lines': lines_with_aliases,
    })

    return render(request, 'get_oee.html', context)


@csrf_exempt
def get_oee_ajax(request):

    line = json.loads(request.POST.get('line'))
    dates = json.loads(request.POST.get('dates'))
    shifts = json.loads(request.POST.get('shifts'))

    output_data = {}

    line_number_of_shifts = 0
    line_time_sum = 0

    output_data[line] = {}

    for date in dates:
        date_time_sum = 0
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        output_data[line][str(date)] = {}

        for shift in shifts:
            output_data[line][str(date)][shift] = {}

            production_data = {} 
            
            if shift == "Morning":

                datetime_shift_start = datetime.datetime.combine(date, datetime.time(6, 0, 0))
                datetime_shift_end = datetime.datetime.combine(date, datetime.time(14, 0, 0))
                shift = "Ranní"

            if shift == "Afternoon":

                datetime_shift_start = datetime.datetime.combine(date, datetime.time(14, 0, 0))
                datetime_shift_end = datetime.datetime.combine(date, datetime.time(22, 0, 0))
                shift = "Odpolední"

            if shift == "Night":

                datetime_shift_start = datetime.datetime.combine(date, datetime.time(22, 0, 0))
                datetime_shift_end = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(6, 0, 0))
                shift = "Noční"


            line_date_shift_production = Smartkpi.objects.filter(machine=line, productiontime__gte=datetime_shift_start, productiontime__lte=datetime_shift_end)

            shift_time_sum = 0

            for production_order in line_date_shift_production.exclude(ordernumber='').values_list('ordernumber', flat=True).distinct():
                production_data[production_order] = defaultdict(int)
                production_data[production_order]['pieces'] = line_date_shift_production.filter(ordernumber=production_order).aggregate(total=Sum(Cast('ispartok', IntegerField())))['total']
                try:
                    production_data[production_order]['tgmax'] = get_tgmax(request=None, ordernumber=production_order)
                except:
                    production_data[production_order]['tgmax'] = 0
                production_data[production_order]['time'] = production_data[production_order]['pieces'] * production_data[production_order]['tgmax']
                shift_time_sum += production_data[production_order]['time']

                output_data[line][str(date)][shift] = dict(production_data)

                output_data[line][str(date)][shift]['oee'] = (shift_time_sum / (8*3600))

                output_data[line][str(date)] = dict(sorted(output_data[line][(str(date))].items(), reverse=True))

                output_data[line] = dict(sorted(output_data[line].items()))

            date_time_sum += shift_time_sum

        line_time_sum += date_time_sum

        new_dict = {k: v for k, v in output_data[line][str(date)].items() if bool(v)}

        output_data[line][str(date)] = new_dict

        try:
            output_data[line][str(date)]['oee'] = date_time_sum / (len(output_data[line][str(date)]) * 8 * 3600)
        except:
            output_data[line].pop(str(date), None)

        output_data[line] = {k: v for k, v in output_data[line].items() if bool(v)}

    for date, other in output_data[line].items():
        for shift, other in other.items():
            if not shift == 'oee':
                line_number_of_shifts += 1
    
    try:
        output_data[line]['oee'] = line_time_sum / (line_number_of_shifts * 8 * 3600)
    except:
        output_data.pop(line)
    
    output_data['line_number_of_shifts'] = line_number_of_shifts
    output_data['line_time_sum'] = line_time_sum

    return JsonResponse(output_data)


def show_production_advisor(request):

    lines = ['KBLIBADBMachineThing', 'KBLIBAoHMachineThing', 'KBLIBBSMachineThing',  'KBLIBDMC80H-OC18BMachineThing', 'KBLIBDMC80H-OC18EMachineThing', 'KBLIBDMC80H-OC18FMachineThing', 'KBLIBDMC80H-OC18GMachineThing', 'KBLIBDMC80H-OC18HMachineThing', 'KBLIBDMC80H-OC18IMachineThing',  'KBLIBDMC80H-OC18JMachineThing', 'KBLIBDMC80H-OC19AMachineThing', 'KBLIBDPAMachineThing', 'KBLIBFP08-Bayonet2MachineThing', 'KBLIBFP09-Lanico2MachineThing', 'KBLIBFP1_2MachineThing', 'KBLIBFP-BayonetMachineThing', 'KBLIBFP-LanicoMachineThing', 'KBLIBKBEMachineThing', 'KBLIBNG4MachineThing', 'KBLIBOBC-1MachineThing', 'KBLIBOBC-2MachineThing', 'KBLIBOBC-3MachineThing', 'KBLIBVGMachineThing', 'KBLIBWedgeMachineThing']

    context = {
        'lines': lines,
    }


    return render(request, 'production_advisor.html', context)


def ajax_parts_to_production_advisor(request):

    return_dict = {}

    # datetime_from = json.loads(request.POST.get('datetime_from'))

    datetime_from = datetime.datetime(2020, 12, 8, 6, 0, 0)
    datetime_to = datetime.datetime.now()

    latest_machine_order = list(Smartkpi.objects.filter(productiontime__gte=datetime_from, productiontime__lte=datetime_to).exclude(ordernumber__in=['Kalibrace', 'dummy_ok', 'dummy_no']).values('ordernumber', 'machine').annotate(Max('productiontime')).values('productiontime__max', 'ordernumber', 'machine').order_by('-productiontime__max'))
        
    latest_machines = []
    latest_orders = []

    for d in latest_machine_order:
        if not d['machine'] in latest_machines:
            latest_orders.append(d['ordernumber'])
            latest_machines.append(d['machine'])
    
    parts_queryset = Smartkpi.objects.filter(productiontime__gte=datetime_from, productiontime__lte=datetime_to, ordernumber__in=latest_orders).values('machine', 'ordernumber').annotate(total_ok_parts=Sum(Cast('ispartok', IntegerField()))).annotate(total_parts=Count(Cast('ispartok', IntegerField())))

    for machine_result in list(reversed(parts_queryset)):
        if not machine_result['machine'] in return_dict:
            return_dict[machine_result['machine']] = {}
            return_dict[machine_result['machine']]['ok'] = machine_result['total_ok_parts']
            return_dict[machine_result['machine']]['nok'] = machine_result['total_parts'] - machine_result['total_ok_parts']
            return_dict[machine_result['machine']]['order'] = machine_result['ordernumber']
            return_dict[machine_result['machine']]['previous_orders'] = []
        else:
            return_dict[machine_result['machine']]['previous_orders'].append(machine_result['ordernumber'])

    return JsonResponse(return_dict)


def ajax_target_delta(request):

    order_numbers = request.POST.get('orders').split(",")

    all_stored_orders = list(OrderStart.objects.values_list('ordernumber', flat=True).distinct())
    unstored_orders = list(set(order_numbers).difference(set(all_stored_orders)))
    stored_orders = list(set(order_numbers).difference(set(unstored_orders)))

    return_dict = {}

    if unstored_orders:
        scheduled_start_for_unstored_order = Smartkpiprocessfloatdata.objects.filter(ordernumber__in=unstored_orders).values('ordernumber', 'productiontime').latest('productiontime')
        return_dict[scheduled_start_for_unstored_order['ordernumber']] = {}
        return_dict[scheduled_start_for_unstored_order['ordernumber']]['start'] = str(scheduled_start_for_unstored_order['productiontime']).replace(" ","T")
        order_start, created = OrderStart.objects.get_or_create(ordernumber=scheduled_start_for_unstored_order['ordernumber'], order_start=scheduled_start_for_unstored_order['productiontime'])

    scheduled_starts_for_stored_orders = OrderStart.objects.filter(ordernumber__in=stored_orders).values('ordernumber', 'order_start')

    for d in scheduled_starts_for_stored_orders:
        return_dict[d['ordernumber']] = {}
        return_dict[d['ordernumber']]['start'] = str(d['order_start']).replace(" ","T")

    apo_times = Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=order_numbers, propertykey='ProcessingTimeAPO-0010').values('ordernumber', 'floatvalue', 'textvalue')

    for d in apo_times:
        try:
            return_dict[d['ordernumber']]['apo'] = d['floatvalue'] if (d['textvalue'] == "SEC") else (d['floatvalue'] * 60)
        except:
            pass

    setup_times = Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=order_numbers, propertykey='SetupTimeAPO-0010').values('ordernumber', 'floatvalue', 'textvalue')

    for d in setup_times:
        try:
            return_dict[d['ordernumber']]['setup'] = d['floatvalue'] if (d['textvalue'] == "SEC") else (d['floatvalue'] * 60)
        except:
            pass

    return JsonResponse(return_dict)


@csrf_exempt
def excel_api_order_info(request):

    order_number = request.POST.get('order', '')
    keyword = request.POST.get('keyword', 'fp09_24')
    interval = int(request.POST.get('interval', 0))
    day = datetime.datetime.strptime(request.POST.get('day'), '%d.%m.%Y')

    filters = {}

    if interval:
        filters['productiontime__gte'] = datetime.datetime.now() - datetime.timedelta(minutes=interval)
    filters['ordernumber'] = order_number

    if keyword == "pieces":
        resp = Smartkpi.objects.filter(**filters).count()

    if keyword == "fp09_24":
        resp = Smartkpi.objects.filter(machine='KBLIBFP09-Lanico2MachineThing', productiontime__gte=day, productiontime__lt=day + datetime.timedelta(days=1)).aggregate(total=Sum(Cast('ispartok', IntegerField())))['total'] or 0

    if keyword == "start":
        resp = Smartkpi.objects.filter(ordernumber=order_number).earliest('productiontime').productiontime
        return HttpResponse(resp)

    if keyword == "last_part":
        resp = Smartkpi.objects.filter(ordernumber=order_number).latest('productiontime').productiontime
        return HttpResponse(resp)

    if keyword == "ok_parts":
        resp = Smartkpi.objects.filter(**filters).aggregate(total=Sum(Cast('ispartok', IntegerField())))['total']

    if keyword == "nok_parts":
        resp = Smartkpi.objects.filter(**filters).count() - Smartkpi.objects.filter(**filters).aggregate(total=Sum(Cast('ispartok', IntegerField())))['total']

    if keyword == "average_production_time":
        time_diffs = []
        produced_parts = list(Smartkpi.objects.filter(**filters).order_by('productiontime').values_list('productiontime', flat=True))
        for num, time in enumerate(produced_parts):
            if not num == 0:
                time_diffs.append((produced_parts[num] - produced_parts[num-1]).total_seconds())

        resp = sum(time_diffs) / len(time_diffs)

    return HttpResponse(int(resp))


@csrf_exempt
def production_file(request):

    uploaded_file = request.FILES['upload_file']

    with open(settings.MEDIA_ROOT + '/' + 'test.txt', 'w') as f:
        myfile = File(f)
        for row in uploaded_file.readlines():
            myfile.write(row.decode('utf-8'))

    return HttpResponse('okay')


@csrf_exempt
def operators_on_line(request):

    machine = request.POST.get('machine')

    operators_checks = Smartkpimachinemessagedata.objects.filter(creationtime__gte=datetime.datetime.now() - datetime.timedelta(days=1), messagetype1="STAFF", machine=machine).exclude(description='Auto log out end of shift').values_list()

    checked_operators = list(operators_checks.values_list('message', flat=True))

    return JsonResponse([list(operators_checks), checked_operators], safe=False)


@csrf_exempt
def get_shift_calendar(request):

    machine = request.POST.get('machine')

    list_of_data = []
    

    if 'PromoticStation' in machine:
        machine = machine.replace('PromoticStation', 'Machine')

    current_shift_beginning = datetime.datetime(year=2021, month=3, day=15, hour=6, minute=0, second=0)
    current_shift_end = datetime.datetime(year=2021, month=3, day=15, hour=14, minute=0, second=0)

    shift_period = Shiftcalendar.objects.filter(starttime__gte=current_shift_beginning, endtime__lte=current_shift_end, machine=machine).order_by('starttime')

    for _ in shift_period:
        data = {}
        data['current_state'] = _.qualifier
        data['beginning_of_state'] = _.starttime
        data['end_of_state'] = _.endtime
        data['shift'] = _.name
        list_of_data.append(data)

    print(list_of_data)

    return JsonResponse(json.dumps(list_of_data, sort_keys=True, indent=1, cls=DjangoJSONEncoder), safe=False)


def shift_screen(request):

    lines_with_aliases = [('KBLIBADBPromoticStationThing', 'ADB'), ('KBLIBAoHPromoticStationThing', 'AoH'), ('KBLIBBSPromoticStationThing', 'BS'), ('KBLIBDMC80H-OC18AStationThing', 'DMC80H-OC18A'), ('KBLIBDMC80H-OC18BMachineThing', 'DMC80H-OC18B'), ('KBLIBDMC80H-OC18CMachineThing', 'DMC80H-OC18C'), ('KBLIBDMC80H-OC18DMachineThing', 'DMC80H-OC18D'), ('KBLIBDMC80H-OC18EMachineThing', 'DMC80H-OC18E'), ('KBLIBDMC80H-OC18FMachineThing', 'DMC80H-OC18F'), ('KBLIBDMC80H-OC18GMachineThing', 'DMC80H-OC18G'), ('KBLIBDMC80H-OC18HMachineThing', 'DMC80H-OC18H'), ('KBLIBDMC80H-OC18IMachineThing', 'DMC80H-OC18I'), ('KBLIBDMC80H-OC18JMachineThing', 'DMC80H-OC18J'), ('KBLIBDMC80H-OC18KMachineThing', 'DMC80H-OC18K'), ('KBLIBDMC80H-OC19AMachineThing', 'DMC80H-OC19A'), ('KBLIBDPAMachineThing', 'DPA'), ('KBLIBFP08-Bayonet2PromoticStationThing', 'FP08-Bayonet2'), ('KBLIBFP09-Lanico2MachineThing', 'FP09-Lanico2'), ('KBLIBFP1_2MachineThing', 'FP1_2'), ('KBLIBFP-BayonetMachineThing', 'FP-Bayonet'), ('KBLIBFP-LanicoMachineThing', 'FP-Lanico'), ('KBLIBKBEMachineThing', 'KBE'), ('KBLIBMCMachineThing', 'MC'), ('KBLIBNG4MachineThing', 'NG4'), ('KBLIBOBC-1MachineThing', 'OBC-1'), ('KBLIBOBC-2MachineThing', 'OBC-2'), ('KBLIBOBC-3MachineThing', 'OBC-3'), ('KBLIBSMMachineThing', 'SM'), ('KBLIBVGMachineThing', 'VG'), ('KBLIBWedgeMachineThing', 'Wedge')]

    context = {
        'lines': lines_with_aliases,
    }

    return render(request,  'shift_screen.html', context)


def get_production_plan_time(request):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    month = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M').month

    smart_kpi_data_order_numbers = Smartkpi.objects.filter(productiontime__gte=start_date, productiontime__lte=end_date).exclude(ordernumber__in=['', '11111111', 'dummy_ok', 'kalibrace']).values_list('ordernumber', flat=True).distinct()

    smart_kpi_data = Smartkpi.objects.filter(ordernumber__in=smart_kpi_data_order_numbers, productiontime__gte=start_date, productiontime__lte=end_date).values('ordernumber', 'partnumber', 'ispartok', 'machine')

    smart_kpi_data_aggregated = smart_kpi_data.values('ordernumber', 'machine', 'partnumber').annotate(total_ok_parts=Sum(Cast('ispartok', IntegerField()))).annotate(total_parts=Count('ispartok'))

    for row in smart_kpi_data_aggregated:
        DLP3.objects.update_or_create(ordernumber=row['ordernumber'], month=month, defaults={'produced_ok_parts': row['total_ok_parts'], 'total_produced_parts': row['total_parts'], 'produced_nok_parts': row['total_parts'] - row['total_ok_parts'], 'machine': row['machine'], 'partnumber': row['partnumber']})

    order_key_value_data = Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=smart_kpi_data_order_numbers, propertykey1__in=['Machine', 'ProcessingTime','SetupTime','SetupTimeCO','ProcessingTimeCO','SetupTimeAPO','ProcessingTimeAPO','tgMaxTime']).values('ordernumber', 'floatvalue', 'textvalue', 'propertykey', 'propertykey1')

    orders_starts_dict = {}

    order_starts_query = Smartkpi.objects.filter(ordernumber__in=smart_kpi_data_order_numbers).values('ordernumber', 'productiontime').order_by('productiontime')

    for row in order_starts_query:
        if row['ordernumber'] in orders_starts_dict:
            continue
        else:
            orders_starts_dict[row['ordernumber']] = row['productiontime']

    orders = DLP3.objects.filter(month=month)

    data = []

    for order in orders:
        if order_key_value_data.filter(ordernumber=order.ordernumber):
            order.processing_time = (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='ProcessingTime', textvalue='MIN').aggregate(processing_time_sum=Sum('floatvalue'))['processing_time_sum'] or 0) + (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='ProcessingTime', textvalue='SEC').aggregate(processing_time_sum=Sum('floatvalue'))['processing_time_sum'] or 0) / 60
            order.processing_time_co = (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='ProcessingTimeCO', textvalue='MIN').aggregate(processing_time_co_sum=Sum('floatvalue'))['processing_time_co_sum'] or 0) + (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='ProcessingTimeCO', textvalue='SEC').aggregate(processing_time_co_sum=Sum('floatvalue'))['processing_time_co_sum'] or 0) / 60
            order.processing_time_apo = (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='ProcessingTimeAPO', textvalue='MIN').aggregate(processing_time_apo_sum=Sum('floatvalue'))['processing_time_apo_sum'] or 0) + (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='ProcessingTimeAPO', textvalue='SEC').aggregate(processing_time_apo_sum=Sum('floatvalue'))['processing_time_apo_sum'] or 0) / 60
            order.setup_time = (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='SetupTime', textvalue='MIN').aggregate(setup_time_sum=Sum('floatvalue'))['setup_time_sum'] or 0) + (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='SetupTime', textvalue='SEC').aggregate(setup_time_sum=Sum('floatvalue'))['setup_time_sum'] or 0) / 60
            order.setup_time_co = (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='SetupTime', textvalue='MIN').aggregate(setup_time_co_sum=Sum('floatvalue'))['setup_time_co_sum'] or 0) + (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='SetupTime', textvalue='SEC').aggregate(setup_time_co_sum=Sum('floatvalue'))['setup_time_co_sum'] or 0) / 60
            order.setup_time_apo = (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='SetupTime', textvalue='MIN').aggregate(setup_time_apo_sum=Sum('floatvalue'))['setup_time_apo_sum'] or 0) +  (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='SetupTime', textvalue='SEC').aggregate(setup_time_apo_sum=Sum('floatvalue'))['setup_time_apo_sum'] or 0) / 60
            order.tgmax_time = (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='tgMaxTime', textvalue='MIN').aggregate(tgmax_time_sum=Sum('floatvalue'))['tgmax_time_sum'] or 0) +  (order_key_value_data.filter(ordernumber=order.ordernumber, propertykey1='tgMaxTime', textvalue='SEC').aggregate(tgmax_time_sum=Sum('floatvalue'))['tgmax_time_sum'] or 0) / 60
            order.order_start = orders_starts_dict[order.ordernumber]
            order.save()

    
    context = {
        'smart_kpi_data_aggregated': smart_kpi_data_aggregated,
        'data': data,
    }


    return render(request, 'production_plan_time.html', context)


def shift_factor(request):

    machine = request.GET.get('machine')
    partnumber = request.GET.get('partnumber')
    station = Smartkpi.objects.filter(machine=machine).last().station

    print(station)

    parts = Smartkpi.objects.filter(machine=machine, partnumber=partnumber, productiontime__gte='2021-05-20').order_by('productiontime')

    parts_with_details = []

    for part in parts:
        part_details = [part.productiontime, part.productiontime] # start of the production
        parts_with_details.append(part_details)

    for idx, part_details in enumerate(parts_with_details):
        if not idx == 0:
            part_details[0] = parts_with_details[idx - 1][1]

    parts_with_details_extended = []

    for part_details in parts_with_details:
        part_with_details = {}
        part_with_details['production_time'] = (part_details[1] - part_details[0]).total_seconds()
        part_with_details['production_end'] = part_details[1]
        part_with_details['number_of_operators'] = 0
        parts_with_details_extended.append(part_with_details)

    op_info = how_many_operators_at_time(parts_with_details[0][0], parts_with_details[-1][0], station)

    return render(request, 'shiftfactor.html', {'op_info': op_info})


def how_many_operators_at_time(start_time, end_time, machine):    

    log_data = Smartkpimachinemessagedata.objects.filter(machine=machine, creationtime__gt=start_time - datetime.timedelta(days=1), creationtime__lt=end_time).order_by('messagetime').exclude(description='All Operator logged out from Station')

    log_dict = {}

    for entry in log_data:
        log_dict[entry.messagetime] = (entry.description, entry.message)

    for key, value in log_dict.items():
        if not value == ('Auto log out end of shift', 'Logout'):
            log_dict.pop(key)
        else:
            break

    return log_dict


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


@csrf_exempt
def SAP_APO_comparison(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        machine_change = request_data['machine_change']
        if machine_change == 1:
            machine = request_data['machine']
            partnumbers = list(Smartkpi.objects.filter(machine=machine).all().values_list('partnumber', flat=True).distinct())
            partnumbers2 = []
            for partnumber in partnumbers:
                if partnumber == None:
                    print('None')
                elif " " in partnumber:
                    print(" ")
                elif len(partnumber) > 3:
                    partnumbers2.append(partnumber)

            return_data = {'partnumbers': partnumbers2}
        elif machine_change == 0:
            machine = request_data['machine']
            MachineDowntimes = request_data['machine_downtimes']
            data_percentage = request_data['data_percentage']
            partnumber = request_data['partnumber']
            ordernumber = list(Smartkpi.objects.filter(machine=machine, partnumber=partnumber).values_list('ordernumber', flat=True).distinct())
            productiontimes = list(Smartkpi.objects.filter(machine=machine, partnumber=partnumber, productiontime__gte = '2021-06-21').order_by('productiontime').values_list('productiontime', 'numberofparts'))
            TgMax = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=ordernumber, propertykey='tgMaxTime-0010').values_list('floatvalue', 'textvalue'))
            SAPAPO = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=ordernumber, propertykey='ProcessingTimeAPO-0010').values_list('floatvalue', 'textvalue'))
            if MachineDowntimes == "Include":
                production = []
                for count, value in enumerate(productiontimes):
                    if count == 0:
                        print('do nothing')
                    else:
                        production_start = productiontimes[count-1][0]
                        production_end = productiontimes[count][0]
                        numberparts = productiontimes[count][1]
                        production_time = production_end - production_start
                        if production_start < production_end:
                            production.append([production_start, production_end, numberparts, production_time])
                order_started = productiontimes[0][0]
                order_ended = productiontimes[-1][0]
                try:
                    station_machine = MachinesConverter.objects.filter(machine_name = machine).first().station_name
                except:
                    station_machine = '0'
                machinestatusdata = list(Smartkpimachinestatusdata.objects.filter(machine__in=[machine, station_machine], statustime__gte = order_started-datetime.timedelta(minutes=60), statustime__lte = order_ended + datetime.timedelta(minutes=60)).order_by('statustime').values_list('status', 'statustime'))
                unproductive_times = []
                for count, value in enumerate(machinestatusdata):
                    if count == 0:
                        print('do nothing')
                    else:
                        if machinestatusdata[count][0] != 'KBMaschStatus.1.Productive':
                            machine_status_start = machinestatusdata[count-1][1]
                            machine_status_end = machinestatusdata[count][1]
                            unproductive_times.append([machine_status_start, machine_status_end])
                ProductiveTimes = []
                NumberOfParts = []
                for production_start, production_end, numberparts, production_time in production:
                    unproduction_time_by_machine = datetime.timedelta(seconds=0)
                    for machine_status_start, machine_status_end in unproductive_times:
                        if machine_status_end > production_start and machine_status_end < production_end and machine_status_start < production_start:
                            unproduction_time_by_machine += machine_status_end - production_start
                        elif machine_status_start > production_start and machine_status_end < production_end:
                            unproduction_time_by_machine += machine_status_end - machine_status_start
                        elif machine_status_start < production_end and machine_status_start > production_start and machine_status_end > production_end:
                            unproduction_time_by_machine += production_end - machine_status_start
                    if numberparts != 0:
                        if SAPAPO[0][1] == 'SEC':
                            ProductiveTimes.append(((production_end-production_start-unproduction_time_by_machine)/numberparts).total_seconds())
                        else:
                            ProductiveTimes.append(((production_end-production_start-unproduction_time_by_machine)/numberparts).total_seconds()/60)
                        NumberOfParts.append(numberparts)
                NumberOfPartsSum = sum(NumberOfParts)
            else:
                NumberOfParts = []
                ProductiveTimes = []
                if SAPAPO[0][1] == 'SEC':
                    unit = 1
                else:
                    unit = 60
                for count, value in enumerate(productiontimes):
                    production_start = productiontimes[count-1][0]
                    production_end = productiontimes[count][0]
                    numberparts = productiontimes[count][1]
                    production_time = production_end - production_start
                    if production_start < production_end:
                        ProductiveTimes.append(production_time.total_seconds()/unit)
                        NumberOfParts.append(numberparts)
                NumberOfPartsSum = sum(NumberOfParts)
            DataPercentage = statistics.quantiles(ProductiveTimes, n=101)
            PercentageOfData = int(data_percentage)
            i = int((100 - PercentageOfData) / 2)
            if i == 0:
                ProductiveTimesWithoutExtreme = ProductiveTimes
                NumberOfPartsWithoutExtreme = NumberOfParts
            else:
                SmallerPercentage = DataPercentage[i]
                BiggerPercentage = DataPercentage[100-i]
                ProductiveTimesWithoutExtreme = []
                NumberOfPartsWithoutExtreme = []
                for productivetime, numberofparts in zip(ProductiveTimes, NumberOfParts):
                    if productivetime > BiggerPercentage or productivetime < SmallerPercentage:
                        continue
                    else:
                        ProductiveTimesWithoutExtreme.append(productivetime)
                        NumberOfPartsWithoutExtreme.append(numberofparts)

            MinProductionTime = min(ProductiveTimesWithoutExtreme)
            MaxProductionTime = max(ProductiveTimesWithoutExtreme)+0.001
            delta = (MaxProductionTime - MinProductionTime) / 20
            intervals = []
            numberofpartsininterval = []
            for i in range(0,20):
                partsininterval = 0
                Start = MinProductionTime + i*delta
                End = MinProductionTime + (i+1)*delta
                intervals.append(f'{round(Start,2)}-{round(End,2)}')
                for productivetime, numberofparts in zip(ProductiveTimesWithoutExtreme, NumberOfPartsWithoutExtreme):
                    if productivetime >= Start and productivetime < End:
                        partsininterval += numberofparts
                numberofpartsininterval.append(partsininterval)
            NumberOfPartsDisplayed = sum(numberofpartsininterval)
            MeanOfProductiveTimesWithoutExtreme = round(statistics.mean(ProductiveTimesWithoutExtreme),2)
            MeanOfProductiveTimes = round(statistics.mean(ProductiveTimes),2)
            MedianOfProductiveTimesWithoutExtreme = round(statistics.median(ProductiveTimesWithoutExtreme),2)
            MedianOfProductiveTimes = round(statistics.median(ProductiveTimes), 2)
            TgMax = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=ordernumber, propertykey='tgMaxTime-0010').values_list('floatvalue', 'textvalue'))
            SAPAPO = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=ordernumber, propertykey='ProcessingTimeAPO-0010').values_list('floatvalue', 'textvalue'))
            return_data = { 'intervals': intervals,
                            'numberofpartsininterval': numberofpartsininterval,
                            'partnumber': partnumber,
                            'numberofpartsdisplayed': NumberOfPartsDisplayed,
                            'numberofpartssum': NumberOfPartsSum,
                            'meanofproductivetimes': MeanOfProductiveTimes,
                            'meanofproductivetimeswithoutextreme': MeanOfProductiveTimesWithoutExtreme,
                            'tgmax': TgMax[0][0],
                            'sapapo': SAPAPO[0][0],
                            'medianofproductivetimes': MedianOfProductiveTimes,
                            'medianofproductivetimeswithoutextreme': MedianOfProductiveTimesWithoutExtreme,
                            'timeunit': SAPAPO[0][1],
                            'productivetimes': ProductiveTimes,
                            'timeunitTgMax': TgMax[0][1],
                           }
        else:
            productiontimes = request_data['productivetimes']
            sapapoperc = float(request_data['sap_apo_perc'])
            sapapopercint = int(sapapoperc) - 1
            DataPercentage = statistics.quantiles(productiontimes, n=101)
            sapapotime = DataPercentage[sapapopercint]
            return_data = {'sapapotime': sapapotime}
        return JsonResponse(return_data)

    if request.method == "GET":
        machines = list(ThingworxLocalsmartkpi.objects.all().values_list('machine', flat=True).distinct())
        machines2 = []
        for machine in machines:
            if machine != None:
                machines2.append(machine)

        context = {
            'machines': machines2
        }
        return render(request, 'sap_apo_comparison.html', context)

@csrf_exempt
def cm_designer(request):

    if request.method == "POST":
        elements = json.loads(request.POST.get('elements'))
        user_url = request.POST.get('user_url')
        canvas_x = request.POST.get('layout_x')
        canvas_y = request.POST.get('layout_y')
        canvas_width = request.POST.get('canvas_width')
        canvas_height = request.POST.get('canvas_height')
        file = request.FILES['picture']
        path = default_storage.save(request.FILES['picture'].name, file)
        
        canvas, created = CMCanvas.objects.update_or_create(user_url=user_url, defaults={'canvas_picture_url': path, 'canvas_x': canvas_x, 'canvas_y': canvas_y, 'canvas_picture_width': canvas_width, 'canvas_picture_height': canvas_height})

        for element in elements:
            CMElement.objects.update_or_create(canvas=canvas, id=int(element[0]), defaults={'from_left': int(float(element[2])), 'from_top': int(float(element[3])), 'plc_tag': element[1]})

        file = request.FILES['picture']
        user_url = request.POST.get('user_url')
        path = default_storage.save(request.FILES['picture'].name, file)


        return HttpResponse("OK")

    return render(request, 'cm_designer.html', {})


def cm_visualizer(request, canvas):

    canvas_object = CMCanvas.objects.get(user_url = canvas)
    canvas_elements = CMElement.objects.filter(canvas = canvas_object)
    
    elements_data = []

    for element in canvas_elements:
        single_element_data = {}
        single_element_data['id'] = element.id
        single_element_data['width'] = int(element.width)
        single_element_data['height'] = int(element.height)
        single_element_data['from_left'] = int(element.from_left)
        single_element_data['from_top'] = int(element.from_top)
        single_element_data['plc_tag'] = element.plc_tag
        elements_data.append(single_element_data)

    context = {
        'canvas': canvas_object,
        'elements': json.dumps(elements_data),
    }

    return render(request, 'cm_visualizer.html', context)


def get_plc_tag_value(request, plc_tag):   

    db_conn = psycopg2.connect(host="10.49.34.115", port="5432", dbname="postgres", user="postgres", password="5teveJo85")
    db_cursor = db_conn.cursor()
    db_cursor.execute("SELECT plc_value FROM plc_test ORDER BY id DESC LIMIT 1")
    response = db_cursor.fetchone()

    return HttpResponse(response)


def prepare_data_master(request):
    try:    
        # last_update = ProductionBoxPlot.objects.latest('start_time').start_time
        last_update = datetime.datetime.strptime('2021-01-01', '%Y-%m-%d')
        period = last_update
    except:
        period = datetime.datetime(2021, 6, 1, 0, 0, 0)

    
    while period < datetime.datetime.now():
        machines = list(MachinesConverter.objects.values_list('machine_name', flat=True))
        #machines = ['KBLIBKBEMachineThing'] #machine_name
        starttime = datetime.datetime.now()
        
        prepare_data_operators(None, period, machines)
        prepare_data_operators_beta(None, period, machines)
        prepare_data_production_beta(None, period, machines)
        prepare_data_box_plot(None, period, machines)
        order_data(None, period, machines)
        print(datetime.datetime.now() - starttime, period)
        period += datetime.timedelta(minutes=15)
        statistical_data(None)

    return HttpResponse("okay")


def prepare_data_operators(request, period=None, machine=None):
    machines = []

    if request:
        period = datetime.datetime.combine(datetime.datetime.strptime(request.GET.get('period'), '%Y-%m-%d'), datetime.time())
        machines.append(request.GET.get('machine', 'KBLIBFP08-Bayonet2MachineThing'))
    else:
        machines.extend(machine)


    LOGOUT_MESSAGES = ["Operator Logout"]

    for machine in machines:
        clock_ins = Smartkpimachinemessagedata.objects.filter(machine=machines_translated(machine, 4), messagetype1='STAFF', messagetime__gte=period - datetime.timedelta(hours=12), messagetime__lt=period + datetime.timedelta(minutes=15)).order_by('messagetime')
        if not clock_ins:
            clock_ins = Smartkpimachinemessagedata.objects.filter(machine=machine, messagetype1='STAFF', messagetime__gte=period - datetime.timedelta(hours=12), messagetime__lt=period + datetime.timedelta(minutes=15)).order_by('messagetime')
        else:
            pass
        workers_at_beggining = []
        workers = []
        for clock_in in clock_ins:
            if period > clock_in.messagetime: 
                if clock_in.messagetype2 == 'Operator Logout':
                    workers = []
                    workers_at_beggining = []
                elif clock_in.messagetype2 == 'Operator':
                    if clock_in.message in workers:
                        workers.remove(clock_in.message)
                    else:
                        workers.append(clock_in.message)
                    if clock_in.message in workers_at_beggining:
                        workers_at_beggining.remove(clock_in.message)
                    else:
                        workers_at_beggining.append(clock_in.message)
            else:
                if clock_in.messagetype2 == 'Operator Logout':
                    workers = []
                elif clock_in.messagetype2 == 'Operator':
                    if clock_in.message in workers:
                        workers.remove(clock_in.message)
                    else:
                        workers.append(clock_in.message)
                OperatorsData.objects.update_or_create(machine=machine, time=clock_in.messagetime, defaults={'number_workers': len(workers)})

        OperatorsData.objects.update_or_create(machine=machine, time=period, defaults={'number_workers': len(workers_at_beggining)})        
        OperatorsData.objects.update_or_create(machine=machine, time=period + datetime.timedelta(minutes=15), defaults={'number_workers': len(workers)})
       


        
        #print(clock_ins)

        #workers = []
        #workers_previous = []
        #print(period)
        #for clock_in in clock_ins:
            #print(clock_in.messagetime, clock_in.message, clock_in.messagetype2)
            #workers_actually = workers
            #if period.strftime("%Y-%m-%d %h:%m:%s") > clock_in.messagetime.strftime("%Y-%m-%d %h:%m:%s"):
                #print("tohle je clock in", clock_in.messagetime,'tohle je period', period, workers)
                #if type(workers_previous) == list:
                    #workers = workers_previous
                    #OperatorsData.objects.update_or_create(machine=machine, time=period, defaults={'number_workers': len(workers)})
                    #workers_previous = "Nothing"  
                    #print("ulozeni prechozich dat")  
                #if "Operator" == clock_in.messagetype2:
                    #if clock_in.message in workers:
                        #workers.remove(clock_in.message)
                        #print('odhlaseni')
                    #else:
                        #workers.append(clock_in.message)
                        #print('prihlaseni')
                    #OperatorsData.objects.update_or_create(machine=machine, time=clock_in.messagetime, defaults={'number_workers': len(workers)})
                #elif clock_in.messagetype2 in LOGOUT_MESSAGES:
                    #workers = []
                    #print('logout')
                    #if len(workers_actually) != len(workers):
                        #OperatorsData.objects.update_or_create(machine=machine, time=clock_in.messagetime, defaults={'number_workers': len(workers)})
            #else:
                #if clock_in.messagetype2 in LOGOUT_MESSAGES:
                    #workers_previous = []
                    #print("logout pred intervalem")
                #elif "Operator" == clock_in.messagetype2:
                    #if clock_in.message in workers_previous:
                        #workers_previous.remove(clock_in.message)
                        #print("odhlaseni pred intervalem")
                    #else:
                        #workers_previous.append(clock_in.message)
                        #print("prihlaseni pred intervalem")

        #if type(workers_previous) == list:
            #workers = workers_previous
            #OperatorsData.objects.update_or_create(machine=machine, time=period, defaults={'number_workers': len(workers)})
            #workers_previous = "Nothing"  
            #print("ulozeni prechozich dat")

        #endtime = period + datetime.timedelta(minutes=15)
        #OperatorsData.objects.update_or_create(machine=machine, time=endtime, defaults={'number_workers': len(workers)})

    return render(request, 'data_operators.html', {'data': clock_ins})


def prepare_data_operators_beta(request, period=None, machine=None):

    machines = []

    if request:
        period = datetime.datetime.strptime(request.GET.get('period'), '%Y-%m-%d')
        machine = request.GET.get('machine', 'KBLIBFP08-Bayonet2MachineThing')
        machines.append(machine)
    else:
        machines.extend(machine)

    #QUARTILE = 900

    date_to = period + datetime.timedelta(minutes=15)

    for machine in machines:

        all_rows = list(OperatorsData.objects.filter(machine=machine, time__gte=period, time__lte=date_to + datetime.timedelta(minutes=15)).distinct('time').order_by('time').values())
        #all_rows_reversed = list(OperatorsData.objects.filter(machine=machine, time__gte=period, time__lte=date_to + datetime.timedelta(minutes=15)).distinct('time').order_by('time').values())

        dict_from_all_rows = {}
        #dict_from_all_rows_reversed = {}

        for item in all_rows:
            dict_from_all_rows[item['time']] = item['number_workers']

        #for item in all_rows_reversed:
            #dict_from_all_rows_reversed[item['time']] = item['number_workers']

        #list_of_quartiles = list(range(int(period.timestamp()), int(date_to.timestamp()), QUARTILE))
        #print('list of quartiles' , list_of_quartiles)
        lenght_of_dict = 0
        for key, value in dict_from_all_rows.items():
            lenght_of_dict += 1
            #number_of_operators = get_number_of_operators_beginning_of_quartile(quartile_start, dict_from_all_rows) or 0
            if key == period:
                number_of_operators = value
        workers_all = 0
        i = 1
        while i < lenght_of_dict:
            next_report = list(dict_from_all_rows.items())[i]
            previous_report_end = next_report[0]
            if previous_report_end > date_to:
                print('Databaze drbe')
                break
            if i == 1:
                workers = number_of_operators * ((previous_report_end - period) / datetime.timedelta(minutes=15))
                workers_all += workers
            else: 
                report = list(dict_from_all_rows.items())[i-1]
                report_start = report[0]
                workers_at_beggining = report[1]
                #print(previous_report_end - report_start)
                workers = workers_at_beggining * ((previous_report_end - report_start ) / datetime.timedelta(minutes=15)) 
                workers_all += workers
                #print(workers_all)
                #print(dict_from_all_rows)
            i += 1
        OperatorsDataEdited.objects.update_or_create(start_time=period, machine=machine, defaults={'number_workers': workers_all, 'end_time': date_to})
        

            
            #if are_there_more_rows_in_quartile(quartile_start, dict_from_all_rows):
                #other_rows_in_quartile = [(k, v) for k,v in dict_from_all_rows_reversed.items() if k > datetime.datetime.fromtimestamp(quartile_start) and k < datetime.datetime.fromtimestamp(quartile_start) + datetime.timedelta(minutes=QUARTILE / 60)]
                #result = 0
                #for idx, other_row in enumerate(other_rows_in_quartile):
                    #if idx == 0:
                        #duration = int((other_row[0] - datetime.datetime.fromtimestamp(quartile_start)).total_seconds())
                        #operators = number_of_operators
                        #result += (duration / QUARTILE) * operators
                    #if idx > 0 and idx < len(other_rows_in_quartile) - 1:
                        #duration = int((other_rows_in_quartile[idx][0] - other_rows_in_quartile[idx-1][0]).total_seconds())
                        #operators = other_rows_in_quartile[idx-1][1]
                        #result += (duration / QUARTILE) * operators
                    #if idx == len(other_rows_in_quartile) - 1:
                        #duration_1 = int((other_rows_in_quartile[idx][0] - other_rows_in_quartile[idx-1][0]).total_seconds())
                        #operators_1 = other_rows_in_quartile[idx-1][1]
                        #duration_2 = int((datetime.datetime.fromtimestamp(quartile_start + QUARTILE) - other_rows_in_quartile[idx][0]).total_seconds())
                        #operators_2 = other_rows_in_quartile[idx][1]
                        #result += (duration_2 / QUARTILE) * operators_2
                        #result += (duration_1 / QUARTILE) * operators_1
                #OperatorsDataEdited.objects.update_or_create(start_time=datetime.datetime.fromtimestamp(quartile_start), machine=machine, defaults={'number_workers': result, 'end_time': datetime.datetime.fromtimestamp(quartile_start + QUARTILE)})
            #else:
                #OperatorsDataEdited.objects.update_or_create(start_time=datetime.datetime.fromtimestamp(quartile_start), machine=machine, defaults={'number_workers': number_of_operators, 'end_time': datetime.datetime.fromtimestamp(quartile_start + QUARTILE)})


    return HttpResponse("OK")


def prepare_data_production_beta(request, period=None, machine=None):

    machines = []

    if request:
        period = datetime.datetime.strptime(request.GET.get('period'), '%Y-%m-%d')
        machine = request.GET.get('machine', 'KBLIBFP08-Bayonet2MachineThing')
        machines.append(machine)
    else:
        machines.extend(machine)

    QUARTILE = 900

    date_to = period + datetime.timedelta(minutes=15)

    for machine in machines:

        all_rows = list(Smartkpi.objects.filter(machine=machine, productiontime__gte=period, productiontime__lte=date_to).exclude(partnumber = '').exclude(ordernumber = '').order_by('-productiontime').values())
        # vynechat Dummy, 11111111, kalibrace...

        dict_from_all_rows = {}

        for item in all_rows:
            dict_from_all_rows[item['productiontime']] = [int(item['ispartok']), item['partnumber'], item['ordernumber']]

        list_of_quartiles = list(range(int(period.timestamp()), int(date_to.timestamp()), QUARTILE))

        for quartile_start in list_of_quartiles:
            quartile_result = 0
            quartile_material = ""
            quartile_order = ""
            for key, value in dict_from_all_rows.items():
                if key >= datetime.datetime.fromtimestamp(quartile_start) and key < datetime.datetime.fromtimestamp(quartile_start + QUARTILE):
                    quartile_result += value[0]
                    quartile_material = value[1]
                    quartile_order = value[2]
            ProductionDataEdited.objects.update_or_create(machine=machine, start_time=datetime.datetime.fromtimestamp(quartile_start), defaults={'material': quartile_material, 'produced_pieces': quartile_result, 'end_time': datetime.datetime.fromtimestamp(quartile_start + QUARTILE), 'order': quartile_order})

    return HttpResponse("OK")


def prepare_data_box_plot(request, period = None, machine = None):

    machines = []

    if request:
        period = datetime.datetime.strptime(request.GET.get('period'), '%Y-%m-%d')
        machine = request.GET.get('machine', 'KBLIBFP08-Bayonet2MachineThing')
        machines.append(machine)
    else:
        machines.extend(machine)

    date_to = period + datetime.timedelta(minutes=15)

    for machine in machines:
        all_operators_data = list(OperatorsDataEdited.objects.filter(machine=machine, start_time__gte=period, end_time__lte=date_to).order_by('-start_time').values())
        all_operators_dict = {}

        for row in all_operators_data:
            all_operators_dict[machine] = {}

        for row in all_operators_data:            
            all_operators_dict[machine][row['start_time']] = row['number_workers']

        all_production_data = list(ProductionDataEdited.objects.filter(machine=machine, start_time__gte=period, end_time__lte=date_to).order_by('-start_time').values_list('machine', 'material', 'produced_pieces', 'start_time', 'end_time', 'order'))
        
        #print(all_operators_dict)

        for row in all_production_data:
            ProductionBoxPlot.objects.update_or_create(machine=row[0], start_time=row[3], defaults={'material': row[1], 'produced_pieces': row[2], 'end_time': row[4], 'number_workers': all_operators_dict[machine][row[3]], 'order': row[5]})
            if row[1] != "":    
                number_of_workers_actual = all_operators_dict[machine][row[3]]
                if row[2] == 0:
                    if int(number_of_workers_actual) > 0.999:
                        print('Na lince ', machine, 'zustal nekdo prihlaseny a nevyrabi se')
                        continue
                find_number_of_workers = list(statisticaldata.objects.filter(material=row[1], Q90__gte=row[2], Q10__lte=row[2], occurrence__gte = 100).values_list('number_workers').order_by('number_workers'))
                find_number_of_workers_x = [i[0] for i in find_number_of_workers]
                if int(number_of_workers_actual) not in find_number_of_workers_x:
                    print('S pravdepodobnosti 80% na lince ', machine, ' nesedi pocet operatoru')
                    continue
                find_number_of_workers = list(statisticaldata.objects.filter(material=row[1], Q75__gte=row[2], Q25__lte=row[2], occurrence__gte = 100).values_list('number_workers').order_by('number_workers'))
                find_number_of_workers_x = [i[0] for i in find_number_of_workers]
                if int(number_of_workers_actual) not in find_number_of_workers_x:
                    print('S pravdepodobnosti 50% na lince ', machine, ' nesedi pocet operatoru')
                    continue
                print("Zde pocet operatoru sedi, nebo je maly vzorek dat ", machine)
            else:
                print(machine, " neznam material")
            


    return HttpResponse("Ok")

def statistical_data(request):
    machines = list(MachinesConverter.objects.values_list('machine_name', flat=True))
    for machine in machines:
        materials = list(ProductionBoxPlot.objects.filter(machine=machine).values_list('material', flat=True).distinct())
        for material in materials:
            workers_dict = {}
            workers = list(ProductionBoxPlot.objects.filter(machine=machine, material=material).order_by('-number_workers').values_list('number_workers', 'produced_pieces'))
            for number_workers, produced_pieces in workers:
                if number_workers == 0 and produced_pieces == 0:
                    pass
                else:
                    if number_workers - (math.floor(number_workers)) == 0 and number_workers > 0:
                        #print("Data", number_workers, produced_pieces)
                        if number_workers not in workers_dict:
                            workers_dict[int(number_workers)] = []
                        workers_dict[int(number_workers)].append(produced_pieces)
            for key, value in workers_dict.items():
                if len(value) > 1:
                    samples = sorted(value)
                    count = len(samples)
                    median = statistics.median(samples)
                    quantiles10s = statistics.quantiles(samples, n=10)
                    quantiles25s = statistics.quantiles(samples, n=4)
                    quantiles10 = quantiles10s[0]
                    quantiles90 = quantiles10s[8]
                    quantiles25 = quantiles25s[0]
                    quantiles75 = quantiles25s[2]
                    statisticaldata.objects.update_or_create(machine=machine, material=material, number_workers=key, defaults={'Q10':quantiles10, 'Q25':quantiles25, 'Q50':median, 'Q75':quantiles75, 'Q90':quantiles90, 'occurrence':count})

    return HttpResponse("Ok")

def order_data(request, period = None, machine = None):
    machines = []

    if request:
        period = datetime.datetime.strptime(request.GET.get('period'), '%Y-%m-%d')
        machine = request.GET.get('machine', 'KBLIBFP08-Bayonet2MachineThing')
        machines.append(machine)
    else:
        machines.extend(machine)

    date = period
    date_end = period + datetime.timedelta(minutes=15)

    order_numbers = list(Smartkpiorderkeyvaluedata.objects.filter(creationtime__gte = date, creationtime__lte = date_end).exclude(ordernumber__icontains='dummy').exclude(ordernumber__icontains='kalibrace').exclude(ordernumber__icontains='111111').values_list('ordernumber', 'textvalue').distinct())
    unique_orders = list(set(str(tup[0]) for tup in order_numbers))
    order_data = list(Smartkpiorderkeyvaluedata.objects.filter(propertykey1__in = ['EarliestScheduledFinishExecution', 'LatestScheduledFinishExecution', 'EarliestScheduledStartProcessing']).values_list('datetimevalue', 'ordernumber').order_by('propertykey1', 'datetimevalue'))
    real_production = list(Smartkpi.objects.filter(ordernumber__in=unique_orders).values_list('ordernumber', 'productiontime').order_by('ordernumber', 'productiontime'))
    real_production_dict = {}
    for item in real_production:
        if not item[0] in real_production_dict:
            real_production_dict[item[0]] = []
            real_production_dict[item[0]].append(item[1])
    for item in real_production[::-1]:
        if not len(real_production_dict[item[0]]) == 2:
            real_production_dict[item[0]].append(item[1])

    shift_details = list(TempSmartkpicvsproductiontargetdetail.objects.annotate(short_order=Substr('ordernumber', 1, 8)).filter(short_order__in=unique_orders).values_list('productiontime', 'shiftfactorinpercent', 'sumplannednumberofworkers', 'short_order').order_by('productiontime'))
    
    order_dict = {}
    for machine in machines:
        machines_list = machines_translated(machine, 3)
        machine_orders_data = [tup[0] for tup in order_numbers if tup[1] in machines_list]
        for order in machine_orders_data:
            if machine not in order_dict:
                order_dict[machine] = {}
            order_time = [tup[0] for tup in order_data if tup[1] == order]
            try:
                OrdersPlanned.objects.update_or_create(machine=machine, order=order, start_time=real_production_dict[order][0], defaults={'end_time': real_production_dict[order][1]})
            except:
                    print('neni shoda')
            if len(order_time) > 2:
                OrdersReality.objects.update_or_create(machine=machine, order=order, start_time=order_time[1], defaults={'end_time': order_time[0]})
            try:
                shift_details2 = [(tup[0], tup[1] * tup[2] / 100, tup[2]) for tup in shift_details if tup[3] == order]
                previous_time = "None"
                for shift_detail in shift_details2:
                    if previous_time == "None":
                        previous_time = shift_detail[0]
                        previous_numberofworkers = shift_detail[1]
                        NumberOfWorkersPlanned.objects.update_or_create(machine=machine, time=shift_detail[0], defaults={'numberofworkers': shift_detail[1], 'plannednumberofworkers': shift_detail[2]})
                    elif (previous_time + datetime.timedelta(minutes=15)) < shift_detail[0] or previous_numberofworkers != shift_detail[1]:
                        previous_time = shift_detail[0]
                        previous_numberofworkers = shift_detail[1]
                        NumberOfWorkersPlanned.objects.update_or_create(machine=machine, time=shift_detail[0], defaults={'numberofworkers': shift_detail[1], 'plannednumberofworkers': shift_detail[2]})
                    else:
                        pass
            except IndexError:
                continue

@csrf_exempt
def charts(request):

    if request.method == "POST":
        data = json.loads(request.body)
        machine = data['machine']
        material = data['material']
        date = datetime.datetime.strptime(data['date'], '%Y-%m-%dT%H:%M')
        date_end = datetime.datetime.strptime(data['date_end'], '%Y-%m-%dT%H:%M')

        x_data = list(OperatorsDataEdited.objects.filter(machine=machines_translated(machine), start_time__gte=date, end_time__lt=date_end).values_list('start_time', 'number_workers').order_by('start_time'))
        y_data = list(ProductionDataEdited.objects.filter(machine=machine, start_time__gte=date, end_time__lt=date_end).values_list('produced_pieces', 'material').order_by('start_time'))
        box_plot_data = ProductionBoxPlot.objects.filter(machine=machine, material=material).values('number_workers', 'produced_pieces').order_by('start_time')
        box_plot_data_y, box_plot_data_x = ([], [])

        for q in box_plot_data:
            if q['number_workers'] - (math.floor(q['number_workers'])) == 0 and q['number_workers'] > 0:
                box_plot_data_y.append(4 * q['produced_pieces'])
                box_plot_data_x.append(q['number_workers'])
        
        count_dict = {}

        for x, y in zip(box_plot_data_x, box_plot_data_y):
            if x not in count_dict:
                count_dict[int(x)] = []
            count_dict[int(x)].append(y)
        
        count_dict2 = {}

        for key, value in count_dict.items():
            count_dict2[key] = len(value)

        annotations_dict = {}

        for workers, output in zip(box_plot_data_x, box_plot_data_y):
            if not workers in annotations_dict:
                annotations_dict[workers] = [output]
            else:
                annotations_dict[workers].append(output)

        for workers, output in annotations_dict.items():
            annotations_dict[workers] = max(output)

        annotations_list = []
        
        for workers, max_output in annotations_dict.items():
            annotation_dict_to_list = {}
            annotation_dict_to_list['x'] = workers
            annotation_dict_to_list['y'] = max_output
            annotation_dict_to_list['xref'] = 'x'
            annotation_dict_to_list['yref'] = 'y'
            annotation_dict_to_list['text'] = count_dict2.get(workers)
            annotation_dict_to_list['ax'] = 0
            annotation_dict_to_list['ay'] = -20
            annotations_list.append(annotation_dict_to_list)

        return_data = {}
        x_data_list = []

        for dt_object in x_data:
            x_data_list.append(str(dt_object))

        production_dictionary = {}
        production_data = list(ProductionBoxPlot.objects.filter(machine=machine, start_time__gte = date, end_time__lte = date_end).values_list('material', 'produced_pieces', 'start_time').order_by('start_time'))
        #print(production_data)
        for multituple in production_data:
            material, produced_pieces, start_time = multituple
            date_string = start_time.strftime("%Y-%m-%d %H")
            if material == "":
                material = "None"
            if (date_string, material) not in production_dictionary:
                production_dictionary[(date_string, material)] = []
            production_dictionary[(date_string, material)].append(produced_pieces)

        for key in production_dictionary:
            production_dictionary[key] = sum(production_dictionary[key])
        #print(production_dictionary)

        materials_list = []
        date_string_list = []
        quantity_list = []
        number_of_materials = []
        for key, value in production_dictionary.items():
            #print(key[0], key[1], value)
            if "None" not in key[1]:
                materials_list.append(key[1])
                date_string_list.append(key[0])
                quantity_list.append(value)
                if key[1] not in number_of_materials:
                    number_of_materials.append(key[1])
        #print(len(number_of_materials))

        dictionary_barchart = {}
        if len(number_of_materials) > 0:
            for material in number_of_materials:
                i = -1
                for material_in_list in materials_list:
                    i += 1
                    if material_in_list == material:
                        if material not in dictionary_barchart:
                            dictionary_barchart[material] = []
                        dictionary_barchart[material].append([date_string_list[i], quantity_list[i]])

        #Comparison of workers and produced pieces
        start_time_comp = [tup[0] for tup in x_data]
        number_operators_comp = [tup[1] for tup in x_data]
        produced_pieces_comp = [tup[0] for tup in y_data]
        material_comp = [tup[1] for tup in y_data]

        #Estimation of workers (pink)
        estimated_number_of_workers_50 = []
        for produced_pieces, material, number_operators in zip(produced_pieces_comp, material_comp, number_operators_comp):
            if produced_pieces != 0:
                find_number_of_workers = list(statisticaldata.objects.filter(material=material, Q75__gte=produced_pieces, Q25__lte=produced_pieces).values_list('number_workers').order_by('number_workers'))
                find_number_of_workers_x = [i[0] for i in find_number_of_workers]
                if int(number_operators) not in find_number_of_workers_x:
                    if len(find_number_of_workers_x) > 0:
                        find_number_of_workers_x = find_number_of_workers_x[0]
                    else:
                        find_number_of_workers = list(statisticaldata.objects.filter(material=material, Q90__gte=produced_pieces, Q10__lte=produced_pieces).values_list('number_workers').order_by('number_workers'))
                        find_number_of_workers_x = [i[0] for i in find_number_of_workers]
                        if len(find_number_of_workers_x) == 0:
                            workers_median = list(statisticaldata.objects.filter(material=material).values_list('number_workers', 'Q50').order_by('number_workers'))
                            difference = 10000
                            for workers, median in workers_median:
                                diff = produced_pieces - median
                                if abs(diff) < difference:
                                    find_number_of_workers_x = workers
                                    difference = abs(diff)
                        else:
                            find_number_of_workers_x = find_number_of_workers_x[0]
                else:
                    find_number_of_workers_x = number_operators
            else:
                find_number_of_workers_x = 0
            estimated_number_of_workers_50.append(find_number_of_workers_x)
        
        #Estimation of workers (red)
        estimated_number_of_workers_80 = []
        for produced_pieces, material, number_operators in zip(produced_pieces_comp, material_comp, number_operators_comp):
            if produced_pieces != 0:
                find_number_of_workers = list(statisticaldata.objects.filter(material=material, Q90__gte=produced_pieces, Q10__lte=produced_pieces).values_list('number_workers').order_by('number_workers'))
                find_number_of_workers_x = [i[0] for i in find_number_of_workers]
                if int(number_operators) not in find_number_of_workers_x:
                    if len(find_number_of_workers_x) > 0:
                        find_number_of_workers_x = find_number_of_workers_x[0]
                    else:
                        workers_median = list(statisticaldata.objects.filter(material=material).values_list('number_workers', 'Q50').order_by('number_workers'))
                        difference = 10000
                        for workers, median in workers_median:
                            diff = produced_pieces - median
                            if abs(diff) < difference:
                                find_number_of_workers_x = workers
                                difference = abs(diff)
                else:
                    find_number_of_workers_x = number_operators
            else:
                find_number_of_workers_x = 0
            estimated_number_of_workers_80.append(find_number_of_workers_x)



        return_data['x'] = [tup[0] for tup in x_data]
        return_data['y_trace1'] = [tup[1] for tup in x_data]
        return_data['y_trace2'] = [tup[0] for tup in y_data]
        return_data['y_trace3'] = estimated_number_of_workers_50
        return_data['y_trace4'] = estimated_number_of_workers_80
        return_data['box_x'] = box_plot_data_x
        return_data['box_y'] = box_plot_data_y
        return_data['annotations'] = annotations_list
        return_data['barchart'] = dictionary_barchart

        return JsonResponse(return_data)


    if request.method == "GET":
        
        context = {'machines': list(Smartkpi.objects.filter(creationtime__gte='2021-01-01', machine__icontains='achine').values_list('machine', flat=True).distinct()),
                    'materials': ProductionBoxPlot.objects.values('material', 'machine').exclude(material__in=[" ", ""]).distinct(),
                    }

    return render(request, 'charts.html', context)

@csrf_exempt
def charts_all(request):
    if request.method == "POST":
        data = json.loads(request.body)
        date = datetime.datetime.strptime(data['date'], '%Y-%m-%dT%H:%M')
        date_end = datetime.datetime.strptime(data['date_end'], '%Y-%m-%dT%H:%M')
        
        charts_data_for_scatter_dict = list(ProductionBoxPlot.objects.filter(start_time__gte = date, end_time__lt = date_end).values_list('machine', 'start_time', 'number_workers', 'produced_pieces', 'material').order_by('machine', 'start_time'))
        machines = list(ProductionBoxPlot.objects.filter(start_time__gte = date, end_time__lt = date_end).exclude(order__isnull=True).exclude(order__exact='').values_list('machine', flat=True).distinct())
        charts_data = list(ProductionBoxPlot.objects.filter(start_time__gte = date, end_time__lt = date_end).exclude(order__isnull=True).exclude(order__exact='').values_list('machine', 'start_time', 'number_workers', 'produced_pieces', 'material', 'order').order_by('machine', 'start_time'))
        #print(charts_data)

        scatter_dict = {}
        workers = {}
        bar_dict = {}
        return_data = {}
        material_time = {}
        order_dict = {}
        machines = []
        production_time_dict_x = {}
        production_time_dict_y = {}

        if len(charts_data) == 0:
            return HttpResponse("Nemam data kokote!")

        for machine, start_time, number_workers, produced_pieces, material in charts_data_for_scatter_dict:
            if machine not in scatter_dict:
                scatter_dict[machine] = []
                machines.append(machine)
            #Estimation of workers (pink)
            if produced_pieces == 0:
                workers50 = 0
                #if number_workers > 0.999:
                    #print('Na lince ', machine, 'zustal nekdo prihlaseny a nevyrabi se')
            elif material == "":
                workers50 = number_workers
            else:
                find_number_of_workers = list(statisticaldata.objects.filter(material=material, Q75__gte=produced_pieces, Q25__lte=produced_pieces).values_list('number_workers', 'occurrence').order_by('occurrence'))
                find_number_of_workers_x = [i[0] for i in find_number_of_workers]
                if int(number_workers) not in find_number_of_workers_x:
                    #print('S pravdepodobnosti 50% na lince ', machine, ' nesedi pocet operatoru')
                    if len(find_number_of_workers_x) > 0:
                        workers50 = find_number_of_workers_x[0]
                    else:
                        workers_median = list(statisticaldata.objects.filter(material=material).values_list('number_workers', 'Q50').order_by('number_workers'))
                        difference = 10000
                        for workers_median, median in workers_median:
                            diff = produced_pieces - median
                            if abs(diff) < difference:
                                workers50 = workers_median
                                difference = abs(diff) 
                else:
                    workers50 = number_workers
            #Estimation of workers (red)
            if produced_pieces == 0:
                workers80 = 0
            elif material == "":
                workers50 = number_workers
            else:
                find_number_of_workers = list(statisticaldata.objects.filter(material=material, Q90__gte=produced_pieces, Q10__lte=produced_pieces).values_list('number_workers', 'occurrence').order_by('occurrence'))
                find_number_of_workers_x = [i[0] for i in find_number_of_workers]
                if int(number_workers) not in find_number_of_workers_x:
                    #print('S pravdepodobnosti 80% na lince ', machine, ' nesedi pocet operatoru')
                    if len(find_number_of_workers_x) > 0:
                        workers80 = find_number_of_workers_x[0]
                    else:
                        workers_median = list(statisticaldata.objects.filter(material=material).values_list('number_workers', 'Q50').order_by('number_workers'))
                        difference = 10000
                        for workers_median, median in workers_median:
                            diff = produced_pieces - median
                            if abs(diff) < difference:
                                workers80 = workers_median
                                difference = abs(diff)
                else:
                    workers80 = number_workers

            scatter_dict[machine].append([start_time, number_workers, produced_pieces, workers50, workers80])
            if machine not in workers:
                workers[machine] = []
            workers[machine].append(number_workers)

        for machine, start_time, number_workers, produced_pieces, material, order in charts_data:
            if machine not in material_time:
                material_time[machine] = {}
            if order not in material_time[machine]:
                try:
                    material_time[machine][order] = [Smartkpiorderkeyvaluedata.objects.filter(propertykey1 = 'ProcessingTimeAPO', ordernumber = order).first().floatvalue if Smartkpiorderkeyvaluedata.objects.filter(propertykey1 = 'ProcessingTimeAPO', ordernumber = order).first().textvalue == "MIN" else Smartkpiorderkeyvaluedata.objects.filter(propertykey1 = 'ProcessingTimeAPO', ordernumber = order).first().floatvalue / 60, 0]
                except:
                    try:
                        order_without_zeros_at_the_beggining = order.lstrip('0')
                        material_time[machine][order] = [Smartkpiorderkeyvaluedata.objects.filter(propertykey1 = 'ProcessingTimeAPO', ordernumber = order_without_zeros_at_the_beggining).first().floatvalue if Smartkpiorderkeyvaluedata.objects.filter(propertykey1 = 'ProcessingTimeAPO', ordernumber = order_without_zeros_at_the_beggining).first().textvalue == "MIN" else Smartkpiorderkeyvaluedata.objects.filter(propertykey1 = 'ProcessingTimeAPO', ordernumber = order_without_zeros_at_the_beggining).first().floatvalue / 60, 0]
                    except:
                        print(order)
                        continue
            if machine not in bar_dict:
                bar_dict[machine] = {}
            if material not in bar_dict[machine]:
                bar_dict[machine][material] = []
            material_time[machine][order][1] += produced_pieces
            bar_dict[machine][material].append([start_time, produced_pieces])

        workers_dict = {k:sum(v) for k,v in workers.items()}
        average_workers = {k:sum(v)/len(v) for k,v in workers.items()}

        totaltime = {}
        for machine in machines:
            if machine in material_time:
                for order in material_time[machine]:
                    time_produced_pieces = material_time[machine][order]
                    time = time_produced_pieces[0] * time_produced_pieces[1]
                    if machine not in totaltime:
                        totaltime[machine] = []
                    totaltime[machine].append(time)
        
        totaltime_dict = {k:sum(v) for k,v in totaltime.items()}

        Orders_Planned = list(OrdersPlanned.objects.filter(start_time__gte = date - datetime.timedelta(days=14), end_time__lte = date_end + datetime.timedelta(days=14)).values_list('machine', 'order', 'start_time', 'end_time').order_by('start_time'))
        Orders_Reality = list(OrdersReality.objects.filter(start_time__gte = date - datetime.timedelta(days=14), end_time__lte = date_end + datetime.timedelta(days=14)).values_list('machine', 'order', 'start_time', 'end_time').order_by('start_time'))
        Number_Of_Workers_Planned = list(NumberOfWorkersPlanned.objects.filter(time__gte = date - datetime.timedelta(days=14), time__lte = date + datetime.timedelta(days=14)).values_list('machine', 'numberofworkers', 'time', 'plannednumberofworkers').order_by('machine','time'))
        order_dict = {}
        production_time_dict_y = {}
        production_time_dict_x = {}
        planned_number_of_workers = {}
        for machine in machines:
            machine_orders = [tup[1] for tup in Orders_Planned if tup[0] == machine]
            for order in machine_orders:
                order_time = [(tup[2], tup[3]) for tup in Orders_Planned if tup[1] == order]
                order_time2 = [(tup[2], tup[3]) for tup in Orders_Reality if tup[1] == order]
                if machine not in order_dict:
                    order_dict[machine] = {}
                if order not in order_dict[machine]:
                    order_dict[machine][order] = []
                try:
                    order_dict[machine][order] = [order_time[0][1], order_time[0][0], 0, order_time2[0][0], order_time2[0][1]]
                except:
                    order_dict[machine][order] = [order_time[0][1], order_time[0][0], 0, "none", "none"]

            number_workers_planned = [(tup[1], tup[2], tup[3]) for tup in Number_Of_Workers_Planned if tup[0] == machine]
            if machine not in production_time_dict_x:
                production_time_dict_x[machine] = []
                production_time_dict_y[machine] = []
                planned_number_of_workers[machine] = []
                time_start = date
            for number_worker_planned in number_workers_planned:
                production_time_dict_x[machine].append(number_worker_planned[1])
                production_time_dict_y[machine].append(number_worker_planned[0])
                previous_number_worker_time = number_worker_planned[2]
                try:
                    if number_worker_planned[1] > time_start and time_start < date_end:
                        if (number_worker_planned[1]) - (time_start) < datetime.timedelta(seconds=1):
                            workers_diff = (date_end - time_start) / (date_end - date) * previous_number_worker_time
                        else:    
                            workers_diff = (number_worker_planned[1] - time_start) / (date_end - date) * previous_number_worker_time
                        planned_number_of_workers[machine].append(workers_diff)
                        time_start = number_worker_planned[1]
                except:
                    pass
        sum_planned_number_of_workers = {k:sum(v) for k,v in planned_number_of_workers.items()}


        return_data['scatter'] = scatter_dict
        return_data['workers'] = workers_dict
        return_data['machines'] = machines
        return_data['bar'] = bar_dict
        return_data['totaltime'] = totaltime_dict
        return_data['order'] = order_dict
        return_data['production_time_x'] = production_time_dict_x
        return_data['production_time_y'] = production_time_dict_y
        return_data['sumplannedworkers'] = sum_planned_number_of_workers
        return_data['averageworkers'] = average_workers
        
    

        #print(return_data)
        return JsonResponse(return_data)

    if request.method == "GET":
        return render(request, 'charts_all.html')

def are_there_more_rows_in_quartile(quartile_start, dict_from_all_rows):
    for key2, value2 in dict_from_all_rows.items():
        if key2 > datetime.datetime.fromtimestamp(quartile_start) and key2 < datetime.datetime.fromtimestamp(quartile_start)  + datetime.timedelta(minutes=15):
            return True
    return False


def get_number_of_operators_beginning_of_quartile(quartile_start, dict_from_all_rows):
    for key, value in dict_from_all_rows.items():
        if key <= datetime.datetime.fromtimestamp(quartile_start):
            return dict_from_all_rows[key]


def make_query_and_write_to_sql(machine, number_workers, time, db_conn, db_cursor):
    query = f"INSERT INTO thingworx_OperatorsData (machine, number_workers, time) VALUES ('{machine}', {number_workers}, '{time}')"
    db_cursor.execute(query)
    db_conn.commit()


def machines_translated(machine_name, version=1):

    #Verze 
    #short_name => machine_name
    #short_name => station_name
    #machine_name => short_name
    #machine_name => station_name
    #station_name => short_name
    #station_name => machine_name

    if version == 1:
        return MachinesConverter.objects.filter(short_name = machine_name).machine_name

    if version == 2:
        return MachinesConverter.objects.filter(short_name = machine_name).station_name

    if version == 3:
        return list(MachinesConverter.objects.filter(machine_name = machine_name).values_list('short_name', flat=True).distinct())
        #Pozor, muzou byt 2 prvky

    if version == 4:
        return MachinesConverter.objects.filter(machine_name = machine_name).first().station_name
    
    if version == 5:
        return list(MachinesConverter.objects.filter(station_name = machine_name).values_list('short_name', flat=True).distinct())

    if version == 6:
        return MachinesConverter.objects.filter(station_name = machine_name).machine_name

    #if version == 1:
    #    try:
    #        random_order_number = Smartkpi.objects.filter(machine=machine_name).first().ordernumber
    #        return Smartkpiprocessfloatdata.objects.filter(ordernumber=random_order_number).first().machine
    #    except:
    #        try:
    #            random_order_number = Smartkpiprocessfloatdata.objects.filter(machine=machine_name).first().ordernumber
    #            return Smartkpi.objects.filter(ordernumber=random_order_number).first().machine
    #        except:
    #            return machine_name

    #if version == 2:
    #    try:
    #        random_order_number = Smartkpiprocessfloatdata.objects.filter(machine=machine_name).first().ordernumber
    #        return Smartkpi.objects.filter(ordernumber=random_order_number).first().machine
    #    except:
    #        try:
    #            random_order_number = Smartkpi.objects.filter(machine=machine_name).first().ordernumber
    #            return Smartkpiprocessfloatdata.objects.filter(ordernumber=random_order_number).first().machine
    #        except:
    #            return machine_name

def shifts_start(hour, now):
    if int(hour) < 6:
        shift_date_start = now - datetime.timedelta(days=1)
        shift_start = shift_date_start.replace(hour=22, minute=0, second=0)
    elif int(hour) < 14:
        shift_start = now.replace(hour=6, minute=0, second=0)
    elif int(hour) < 22:
        shift_start = now.replace(hour=14, minute=0, second=0)
    else:
        shift_start = now.replace(hour=22, minute=0, second=0)
    return shift_start

def last_part(machine, now, shift_start):
    last_ordernumber = "None"
    partnumbers = list(Smartkpi.objects.filter(productiontime__gte=shift_start,productiontime__lte=now, machine=machine).values_list('partnumber', 'ordernumber', 'productiontime').order_by('productiontime'))
    for partnumber, ordernumber, productiontime in partnumbers:
        if ordernumber == last_ordernumber:
            pass
        else:
            last_partnumber = partnumber
            last_ordernumber = ordernumber
            time_of_first_last_product = productiontime
    return last_partnumber, last_ordernumber, time_of_first_last_product

def dlp1_calculation(last_ordernumber, machine):
    production_times = []
    fabricated_parts = list(Smartkpi.objects.filter(machine = machine, ordernumber = last_ordernumber).values_list('ordernumber','productiontime','ispartok','numberofparts').order_by('productiontime'))
    line_statuses_time_start = fabricated_parts[0][1] - datetime.timedelta(hours = 1)
    line_statuses_time_end = fabricated_parts[-1][1]
    line_statuses = list(Smartkpimachinestatusdata.objects.filter(machine = machines_translated(machine, 4), statustype = 'Operator Screen', creationtime__gte = line_statuses_time_start, creationtime__lte = line_statuses_time_end).values_list('creationtime', 'substatus').order_by('creationtime'))
    for index, elem in enumerate(fabricated_parts):
        if (index+1 < len(fabricated_parts) and index - 1 >= 0):
            if fabricated_parts[index+1][2] == True:
                production_time = (fabricated_parts[index+1][1] - fabricated_parts[index][1]).seconds
                for index2, elem2 in enumerate(line_statuses):
                    if (index2+1 < len(line_statuses) and index2 - 1 >= 0):
                        if line_statuses[index2+1][0] > fabricated_parts[index+1][1] and line_statuses[index2][0] < fabricated_parts[index][1]:
                            production_times.append(production_time/fabricated_parts[index+1][3])
    DLP1_estimated = 3600 / median(production_times)
    return DLP1_estimated

def get_time_intervals(time_of_first_last_part, now, machine):
    line_statuses_dict = {}
    line_statuses = list(Smartkpimachinestatusdata.objects.filter(machine = machines_translated(machine, 4), statustype = 'Operator Screen', creationtime__gte = time_of_first_last_part - datetime.timedelta(hours = 1), creationtime__lte = now).values_list('creationtime', 'substatus').order_by('creationtime'))
    for index, elem in enumerate(line_statuses):
        if (index+1 < len(line_statuses) and index - 1 >= 0):
            if line_statuses[index][1] not in line_statuses_dict:
                line_statuses_dict[line_statuses[index][1]] = []
            line_statuses_dict[line_statuses[index][1]].append([line_statuses[index][0], line_statuses[index+1][0]])
        else:
            actual_line_status = line_statuses[index][1]
            actual_line_status_time = line_statuses[index][0]
    if actual_line_status not in line_statuses_dict:
        line_statuses_dict[actual_line_status] = []
    line_statuses_dict[actual_line_status].append([actual_line_status_time, now])
    start_time_iteration = time_of_first_last_part.replace(minute = time_of_first_last_part.minute//15 * 15, second = 0)
    coefficient_in_interval = {}
    while start_time_iteration < now:
        start_time_iteration = start_time_iteration + datetime.timedelta(minutes = 15)
        coefficient_in_interval[start_time_iteration] = []
    for productive_start, productive_end in line_statuses_dict['KBMaschStatus.2.Productive.Start']:
        for key in coefficient_in_interval:
            if (key - datetime.timedelta(minutes = 15)) > productive_start and key < productive_end:
                coefficient_in_interval[key].append(1)
            elif (productive_start > key - datetime.timedelta(minutes = 15)) and productive_start < key:
                if productive_end > key:
                    delta_time = (key - productive_start).seconds
                else:
                    delta_time = (productive_end - productive_start).seconds
                coefficient_in_interval[key].append(delta_time/900)
            elif (productive_end < key and productive_end > key - datetime.timedelta(minutes=15)):
                delta_time = (productive_end - (key - datetime.timedelta(minutes=15))).seconds
                coefficient_in_interval[key].append(delta_time/900)
    coefficient_sum_dict = {k:sum(v) for k,v in coefficient_in_interval.items()}
    return coefficient_sum_dict, actual_line_status, actual_line_status_time

def get_dlp_estimated_intervals(coefficient_of_dlp1_in_timeintervals, dlp1_estimated):
    time_intervals = []
    dlp1_intervals = []
    time_intervals_in_hours_mins = []
    for key in coefficient_of_dlp1_in_timeintervals:
        time_intervals_in_hours_mins.append(key.strftime('%H:%M'))
        time_intervals.append(key)
        dlp1_intervals.append(coefficient_of_dlp1_in_timeintervals[key] * dlp1_estimated)
    return time_intervals, dlp1_intervals, time_intervals_in_hours_mins

def get_dlp_real_time_intervals(time_intervals, last_ordernumber, time_of_first_last_part, now, machine):
    production_real_in_intervals = {}
    dlp1_real_time_intervals = []
    total_production = 0
    rejects = 0
    for time_interval in time_intervals:
        production_real_in_intervals[time_interval] = []
    fabricated_parts = list(Smartkpi.objects.filter(machine = machine, ordernumber = last_ordernumber, creationtime__gte = time_of_first_last_part, creationtime__lte = now).values_list('ordernumber','productiontime','ispartok','numberofparts').order_by('productiontime'))
    for ordernumber, productiontime, ispartok, numberofparts in fabricated_parts:
        for key in production_real_in_intervals:
            if productiontime > (key - datetime.timedelta(minutes=15)) and productiontime <= key:
                if ispartok == True:
                    production_real_in_intervals[key].append(numberofparts*4)
                    total_production += numberofparts
                else:
                    rejects += numberofparts
    dlp1_real_time_in_intervals = {k:sum(v) for k,v in production_real_in_intervals.items()}
    for key in dlp1_real_time_in_intervals:
        dlp1_real_time_intervals.append(dlp1_real_time_in_intervals[key])

    
    return dlp1_real_time_intervals, total_production, rejects

def get_monthly_OEE(machine, now):
    OEE_monthly = list(Smartkpivalues.objects.filter(machine = machine, kpiname = 'CVS: OEE (Version 2)', kpitimebase = 'month', creationtime__gte = now - datetime.timedelta(days = 100)).values_list('kpifloatvalue', 'creationtime').order_by('creationtime'))
    OEE = OEE_monthly[-1][0]
    return OEE 

def get_monthly_RQ(machine, now):
    RQ_monthly = list(Smartkpivalues.objects.filter(machine = machine, kpiname = 'RQ', kpitimebase = 'month', creationtime__gte = now - datetime.timedelta(days = 100)).values_list('kpifloatvalue', 'creationtime').order_by('creationtime'))
    RQ = RQ_monthly[-1][0]
    return RQ

def get_number_of_operators(machine, shift_start, now):
    clock_ins = Smartkpimachinemessagedata.objects.filter(machine=machines_translated(machine, 4), messagetype1='STAFF', messagetime__gte= shift_start, messagetime__lte=now).order_by('messagetime')
    workers_at_beggining = []
    number_workers = []
    time_workers = []
    for clock_in in clock_ins:
        workers_start = len(workers_at_beggining)
        if clock_in.messagetype2 == 'Operator Logout':
            workers_at_beggining = []
        elif clock_in.messagetype2 == 'Operator':
            if clock_in.message in workers_at_beggining:
                workers_at_beggining.remove(clock_in.message)
            else:
                workers_at_beggining.append(clock_in.message)
        workers_end = len(workers_at_beggining)
        if workers_start != workers_end:
            number_workers.append(workers_end)
            time_workers.append(clock_in.messagetime)
    return workers_end, number_workers, time_workers

def get_DLP1_graph(dlp1_real_time_intervals, dlp1_estimated_intervals):
    DLP1_average_shift_real = sum(dlp1_real_time_intervals) / len(dlp1_real_time_intervals)
    DLP1_average_shift_estimated = sum(dlp1_estimated_intervals) / len(dlp1_estimated_intervals)
    return round(DLP1_average_shift_real,1), round(DLP1_average_shift_estimated,1)

def get_OEE_graph(time_of_first_last_part, now, total_production, last_ordernumber, machine, dlp1):
    processing_time = list(TempSmartkpicvsproductiontargetdetail.objects.filter(linethingname=machine, starttime__gte=time_of_first_last_part).annotate(short_order=Substr('ordernumber', 1, 8)).filter(short_order__in=last_ordernumber).values_list('processingtime', 'ordernumber').distinct())
    if len(processing_time) == 0:
        estimated_time = 3600/dlp1 * total_production
    else:
        estimated_time = processing_time[1]*60 * total_production
    OEE = estimated_time / ((now - time_of_first_last_part).seconds)
    return round(OEE, 3)

def get_loss_to_one_part(dlp1_real_time_intervals, dlp1_estimated_intervals, time_intervals_15):
    loss_to_one_part = []
    i = 0
    dlp1_real_4 = 0
    dlp1_estimated_4 = 0
    time_intervals = []
    loss_to_one_part = []
    for dlp1_real_time, dlp1_estimated, time_interval in zip(dlp1_real_time_intervals, dlp1_estimated_intervals, time_intervals_15):
        i += 1
        dlp1_real_4 += dlp1_real_time
        dlp1_estimated_4 += dlp1_estimated
        if i == 4:
            i = 0
            loss_to_one_part.append(3600/dlp1_estimated_4 - 3600/dlp1_real_4)
            time_intervals.append(time_interval)

    return loss_to_one_part, time_intervals

def get_top_5_line_defects(machine, shift_start, now):
    line_describtion = list(Smartkpimachinestatusdata.objects.filter(machine =machines_translated(machine, 4), statustype = 'Operator Screen', creationtime__gte = shift_start, creationtime__lte = now).values_list('creationtime', 'substatus').order_by('creationtime'))
    substatus_dict = {}
    for index, elem in enumerate(line_describtion):
        if (index+1 < len(line_describtion) and index - 1 >= 0):
            end_time = line_describtion[index+1][0]
            start_time = line_describtion[index][0]
            substatus = line_describtion[index][1]
            delta_time_in_seconds = (end_time - start_time).seconds
            if substatus != 'KBMaschStatus.2.Productive.Start':
                if substatus not in substatus_dict:
                    substatus_dict[substatus] = []
                substatus_dict[substatus].append(delta_time_in_seconds)
    substatus_sum_dict = {k:sum(v) for k,v in substatus_dict.items()}
    substatus_sum = 0
    organization_loss = 0
    for key in substatus_sum_dict:
        substatus_sum += substatus_sum_dict[key]
        if key == 'KBMaschStatus.2.OI.Break.479' or key == 'KBMaschStatus.2.TI.5Sactivities.cleaning' or key == 'KBMaschStatus.2.TI.5Sactivities.1stLevelMaintenance':
            organization_loss += substatus_sum_dict[key]
    substatus_percent = (substatus_sum / (now - shift_start).seconds)*100
    substatus_percent_organization = (organization_loss / (now - shift_start).seconds)*100
    substatus_top5 = dict(sorted(substatus_sum_dict.items(), key = itemgetter(1), reverse = True)[:5])
    substatus_names = []
    substatus_time = []
    for key in substatus_top5:
        substatus_names.append(key) 
        substatus_time.append(substatus_top5[key])
    return substatus_names, substatus_time, round(substatus_percent, 1), substatus_percent_organization

def get_top_5_NOK_defects(machine, shift_start, now):
    NOK_defects = list(Smartkpimachinemessagedata.objects.filter(machine=machines_translated(machine, 4), messagetype2 = 'KBMaschMessage.Button.NokPart', creationtime__gte = shift_start, creationtime__lte = now).values_list('messagetype2','message'))
    NOK_defects_dict = {}
    for messagetype2, message in NOK_defects:
        if message not in NOK_defects_dict:
            NOK_defects_dict[message] = []
        NOK_defects_dict[message].append(1)
    NOK_defects_sum_dict = {k:sum(v) for k,v in NOK_defects_dict.items()}
    NOK_defects_top5 = dict(sorted(NOK_defects_sum_dict.items(), key = itemgetter(1), reverse = True)[:5])
    NOK_defects_name = []
    NOK_defects_occurency = []
    rejects_shift = 0
    for key in NOK_defects_top5:
        NOK_defects_name.append(key) 
        NOK_defects_occurency.append(NOK_defects_top5[key])
        rejects_shift += NOK_defects_top5[key]
    return NOK_defects_name, NOK_defects_occurency, rejects_shift

def get_total_production_order(last_ordernumber, machine, now):
    total_production_order = 0
    fabricated_parts = list(Smartkpi.objects.filter(machine = machine, ordernumber = last_ordernumber, productiontime__lte = now).values_list('ordernumber','productiontime','ispartok','numberofparts').order_by('productiontime'))
    time_of_first_product_in_order = fabricated_parts[0][1]
    for ordernumber, productiontime, ispartok, numberofparts in fabricated_parts:
        if ispartok == True:
            total_production_order += numberofparts
    return total_production_order, time_of_first_product_in_order

def get_dlp1_estimated_intervals_without_workers(coefficient_order, dlp1_estimated):
    times = []
    dlp1_intervals = []
    for key in coefficient_order:
        times.append(key)
        dlp1_intervals.append(coefficient_order[key]*dlp1_estimated)
    return dlp1_intervals, times

def translate_top_5_line_defects(top_5_line_defects, machine):
    translated_top_5_line_defects_list = []
    for line_defect in top_5_line_defects:
        try:
            try:
                translated_line_defect = LineFailureTranslation.objects.values_list('localizedstatustext', flat=True).get(level2status=line_defect, station = "all")
            except LineFailureTranslation.DoesNotExist:
                translated_line_defect = LineFailureTranslation.objects.values_list('localizedstatustext', flat=True).get(level2status=line_defect, station = machines_translated(machine, 4))
        except LineFailureTranslation.DoesNotExist:
            translated_line_defect = 'Nespecifikovano'
        translated_top_5_line_defects_list.append(translated_line_defect)
    return translated_top_5_line_defects_list

def translate_actual_line_status(line_status, machine):
    try:
        try:
            translated_line_defect = LineFailureTranslation.objects.values_list('localizedstatustext', flat=True).get(level2status=line_status, station = "all")
        except LineFailureTranslation.DoesNotExist:
            translated_line_defect = LineFailureTranslation.objects.values_list('localizedstatustext', flat=True).get(level2status=line_status, station = machines_translated(machine, 4))
    except LineFailureTranslation.DoesNotExist:
        translated_line_defect = 'Nespecifikovano'
    return translated_line_defect

def translate_top_5_NOK_defects(top_5_NOK_defects, machine):
    translated_top_5_NOK_defects_list = []
    for NOK_defect in top_5_NOK_defects:
        try:
            try:
                translated_NOK_defect = NOKReasonsTranslation.objects.values_list('localizedstatustext', flat=True).get(level2status=NOK_defect, station = "all")
            except NOKReasonsTranslation.DoesNotExist:
                translated_NOK_defect = NOKReasonsTranslation.objects.values_list('localizedstatustext', flat=True).get(level2status=NOK_defect, station = machines_translated(machine, 4))
        except NOKReasonsTranslation.DoesNotExist:
            translated_NOK_defect = 'Nespecifikovano'
        translated_top_5_NOK_defects_list.append(translated_NOK_defect)
    return translated_top_5_NOK_defects_list

def get_estimated_total_shift_production_sap_apo(shift_start, now, machine, processing_time_order, time_of_first_last_part):
    machine_short_name =  machines_translated(machine, 3)[0]
    shift_calendar = list(Shiftcalendar.objects.filter(machine = machine_short_name, starttime__gte = shift_start - datetime.timedelta(hours=1), endtime__lte = now + datetime.timedelta(hours = 8)).exclude(qualifier='P').values_list('starttime', 'endtime', 'qualifier').order_by('starttime'))
    work_times = []
    for start_time, end_time, qualifier in shift_calendar:
        if qualifier == "W":
            if start_time <= now:
                if end_time <= now:
                    if start_time < time_of_first_last_part and end_time > time_of_first_last_part:
                        work_time = end_time - time_of_first_last_part
                        work_times.append(work_time)
                    elif end_time > time_of_first_last_part:
                        work_time = end_time - start_time
                        work_times.append(work_time)
                        
                else:
                    if start_time < time_of_first_last_part and end_time > time_of_first_last_part:
                        work_time = now - time_of_first_last_part
                        work_times.append(work_time)
                    elif end_time > time_of_first_last_part:
                        work_time = now - start_time
                        work_times.append(work_time)
    sum_work_times = sum(work_times, datetime.timedelta(0,0))
    if processing_time_order[0][1] == "SEC":
        processing_time_order_in_datetime = datetime.timedelta(seconds = processing_time_order[0][0])
    estimated_total_shift_production = sum_work_times / processing_time_order_in_datetime
    return estimated_total_shift_production

def get_estimated_total_order_production_sap_apo(scheduled_start, scheduled_end, now, machine, processing_time_order):
    machine_short_name =  machines_translated(machine, 3)[0]
    shift_calendar = list(Shiftcalendar.objects.filter(machine = machine_short_name, starttime__gte = scheduled_start - datetime.timedelta(hours=8), endtime__lte = now + datetime.timedelta(hours = 8)).exclude(qualifier='P').values_list('starttime', 'endtime', 'qualifier').order_by('starttime'))
    work_times = []
    for start_time, end_time, qualifier in shift_calendar:
        if qualifier == "W":
            if scheduled_start < end_time:
                if scheduled_end > end_time:
                    if scheduled_start >= start_time and scheduled_end >= end_time:
                        if end_time > now:
                            end_time = now
                        work_time2 = end_time - scheduled_start
                    elif scheduled_start < start_time:
                        if end_time < now:
                            work_times.append(end_time - start_time)
                        elif start_time < now:
                            work_time = now - start_time
                            work_times.append(work_time)
                elif scheduled_end > start_time:
                    if now > scheduled_end:
                        work_time = scheduled_end - start_time
                        work_times.append(work_time)
                    elif now > start_time and now < scheduled_end:
                        work_time = now - start_time
                        work_times.append(work_time)

    work_times.append(work_time2)
            
    sum_work_times = sum(work_times, datetime.timedelta(0,0))
    if processing_time_order[0][1] == "SEC":
        processing_time_order_in_datetime = datetime.timedelta(seconds = processing_time_order[0][0])
    estimated_total_order_production = sum_work_times / processing_time_order_in_datetime
    return estimated_total_order_production

def edit_dlp1_intervals_by_operators(dlp1_estimated_intervals, time_intervals, number_workers, time_workers, machine, shift_start, now):
    planned_number_of_workers = list(TempSmartkpicvsproductiontargetdetail.objects.filter(linethingname = machine, starttime__gte = shift_start, endtime__lte = now).values_list('starttime', 'endtime', 'sumplannednumberofworkers', 'shiftfactorinpercent'))
    if len(planned_number_of_workers) == 0:
        workers_estimated = number_workers[-1] * 0.9
    else:
        workers_estimated = planned_number_of_workers[0][2] / planned_number_of_workers[0][3] * 100
    log_in_out = shift_start
    workers_coef = []
    for time_interval, estimated_dlp1 in zip(time_intervals, dlp1_estimated_intervals):
        workers_total_seconds = 0
        for time, number in zip(time_workers, number_workers):
            if (time_interval - datetime.timedelta(minutes=15)) < time and time_interval > time:
                delta_time = (time - log_in_out).total_seconds()
                log_in_out = time
                workers_total_seconds += delta_time * number
        delta_time = (time_interval - log_in_out).total_seconds()
        if delta_time > 900:
            delta_time = 900
        workers_total_seconds += delta_time * number
        workers_coef.append(workers_total_seconds/900/workers_estimated)
        log_in_out = time_interval
    dlp1_real_time_intervals_edited = []
    for workers_coefficient, estimated_dlp1 in zip(workers_coef,dlp1_estimated_intervals):
        dlp1_real_time_intervals_edited.append(workers_coefficient*estimated_dlp1)
    return dlp1_real_time_intervals_edited
                
def get_production_time_and_loses(line_defects_percent, organization_loss, shift_start, now, machine):
    fabricated_parts = list(Smartkpi.objects.filter(machine = machine, productiontime__lte = now, productiontime__gte = shift_start).values_list('ordernumber','productiontime','ispartok','numberofparts').order_by('productiontime'))
    parts_dict = {}
    parts_rejects_dict = {}
    total_parts_ok_dict = {}
    for ordernumber, productiontime, ispartok, numberofparts in fabricated_parts:
        if ispartok == 0:
            if ordernumber not in parts_rejects_dict:
                parts_rejects_dict[ordernumber] = []
            parts_rejects_dict[ordernumber].append(numberofparts)
        if ispartok == 1:
            if ordernumber not in total_parts_ok_dict:
                total_parts_ok_dict[ordernumber] = []
            total_parts_ok_dict[ordernumber].append(numberofparts)
        if ordernumber not in parts_dict:
            parts_dict[ordernumber] = []
        parts_dict[ordernumber].append(numberofparts)
    total_parts_dict = {k:sum(v) for k,v in parts_dict.items()}
    total_parts_rejects_dict = {k:sum(v) for k,v in parts_rejects_dict.items()}
    total_parts_ok_dict_sum = {k:sum(v) for k,v in total_parts_ok_dict.items()}
    Production_of_OK_parts = 0
    Quality_loss = 0
    for key in total_parts_dict:
        Processing_time_order = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber = key, propertykey1 = "ProcessingTimeAPO").values_list('floatvalue','textvalue'))
        if key in total_parts_rejects_dict:
            Production_of_OK_parts += Processing_time_order[0][0] * (total_parts_dict[key] - total_parts_rejects_dict[key])
            Quality_loss += Processing_time_order[0][0] * total_parts_rejects_dict[key]
        else:
            Production_of_OK_parts += Processing_time_order[0][0] * total_parts_dict[key]
    Organization_loss = (now - shift_start).total_seconds() * organization_loss/100
    Other_losses = (now - shift_start).total_seconds() * (line_defects_percent - organization_loss)/100
    Performance_loss = (now - shift_start).total_seconds() - (Quality_loss + Production_of_OK_parts + Organization_loss + Other_losses)
    if Performance_loss < 0:
        Performance_loss = 0
    times = [Production_of_OK_parts, Quality_loss, Performance_loss, Organization_loss, Other_losses]
    return times, total_parts_ok_dict_sum

def get_total_production_order_estimated(dlp1_estimated_intervals_order):
    total_production_order_estimated  = sum(dlp1_estimated_intervals_order)/4
    return total_production_order_estimated

def get_target_order(Scheduled_start_order, Scheduled_end_order, time_of_first_last_ordernumber, Processing_time_order, machine, shift_start):
    machine_short_name =  machines_translated(machine, 3)[0]
    if Scheduled_start_order < shift_start:
        Scheduled_start_order = shift_start
    if Scheduled_start_order > time_of_first_last_ordernumber:
        Scheduled_start_order = time_of_first_last_ordernumber
    if Scheduled_end_order > shift_start + datetime.timedelta(hours = 8):
        Scheduled_end_order = shift_start + datetime.timedelta(hours = 8)
    shift_calendar = list(Shiftcalendar.objects.filter(machine = machine_short_name, starttime__gte = Scheduled_start_order, endtime__lte = Scheduled_end_order).exclude(qualifier='P').values_list('starttime', 'endtime', 'qualifier').order_by('starttime'))
    break_times = []
    for start_time, end_time, qualifier in shift_calendar:
        if qualifier == "B":
            break_times.append(end_time - start_time)
    sum_breaks = sum(break_times, datetime.timedelta(0,0))
    total_order_time = (Scheduled_end_order - Scheduled_start_order - sum_breaks).total_seconds()
    if Processing_time_order[0][1] == "SEC":
        total_order_production = total_order_time / Processing_time_order[0][0]
    return round(total_order_production)

def get_target_order_full(Scheduled_start_order, Scheduled_end_order, Processing_time_order, machine):
    machine_short_name =  machines_translated(machine, 3)[0]
    shift_calendar = list(Shiftcalendar.objects.filter(machine = machine_short_name, starttime__gte = Scheduled_start_order, endtime__lte = Scheduled_end_order).exclude(qualifier='P').values_list('starttime', 'endtime', 'qualifier').order_by('starttime'))
    break_times = []
    for start_time, end_time, qualifier in shift_calendar:
        if qualifier == "B":
            break_times.append(end_time - start_time)
    sum_breaks = sum(break_times, datetime.timedelta(0,0))
    total_order_time = (Scheduled_end_order - Scheduled_start_order - sum_breaks).total_seconds()
    if Processing_time_order[0][1] == "SEC":
        total_order_production = total_order_time / Processing_time_order[0][0]
    return round(total_order_production)

def get_estimated_shift_production(machine, total_parts_in_dict, shift_start, now, last_ordernumber, Processing_time_order_of_last_part):
    machine_short_name =  machines_translated(machine, 3)[0]
    shift_calendar = list(Shiftcalendar.objects.filter(machine = machine_short_name, starttime__gte = shift_start, endtime__lte = shift_start + datetime.timedelta(hours=8)).exclude(qualifier='P').values_list('starttime', 'endtime', 'qualifier').order_by('starttime'))
    break_times = []
    estimated_parts = 0
    for start_time, end_time, qualifier in shift_calendar:
        if qualifier == "B":
            break_times.append(end_time - start_time)
    sum_breaks = sum(break_times, datetime.timedelta(0,0))
    total_shift_time = (datetime.timedelta(hours=8) - sum_breaks).total_seconds()
    for key in total_parts_in_dict:
        if key != last_ordernumber:
            Processing_time_order = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber = key, propertykey1 = "ProcessingTimeAPO").values_list('floatvalue','textvalue'))
            if Processing_time_order[0][1] == "SEC":
                total_time = total_parts_in_dict[key] * Processing_time_order[0][0]
                estimated_parts += total_parts_in_dict[key]
                total_shift_time -= total_time
    if Processing_time_order_of_last_part[0][1] == "SEC":
        estimated_parts += total_shift_time / Processing_time_order_of_last_part[0][0]
    return estimated_parts

def get_dlp1_of_last_ordernumber(machine, ordernumber_last):
    production_time = []
    total_parts = 0
    fabricated_parts = list(Smartkpi.objects.filter(machine = machine, ordernumber = ordernumber_last, numberofparts__gte = 1).values_list('ordernumber','productiontime','ispartok','numberofparts').order_by('productiontime'))
    for index, elem in enumerate(fabricated_parts):
        if (index+1 < len(fabricated_parts) and index - 1 >= 0):
            if fabricated_parts[index+1][2] == True:
                if fabricated_parts[index+1][3] >= 1:
                    for i in range(fabricated_parts[index+1][3]):
                        total_parts += 1
                        production_time.append((fabricated_parts[index+1][1] - fabricated_parts[index][1]).seconds / fabricated_parts[index+1][3])
    if len(production_time) == 0:
        return '-', '-'
    return round(3600/median(production_time),2), total_parts

def calculation_dlp1(request):
    #Init
    calculation_datetime_start = datetime.datetime(year=2021, month=11, day=1, hour=0, minute=0, second=0)
    calculation_datetime_end = datetime.datetime(year=2021, month=11, day=11, hour=0, minute=0, second=0)
    interval = 4 # 15 minut = 15, 60 minut = 60, 4 hodiny = 4

    machines_all = list(MachinesConverter.objects.values_list('machine_name', flat=True).distinct())
    
    for machine in machines_all:
        number_of_parts = {}
        orders = {}
        productive_times = []
        time_intervals = {}
        line_describtion = list(ThingworxLocalmachinestatusdata.objects.filter(machine = machines_translated(machine, 4), statustype = 'Operator Screen', creationtime__gte = calculation_datetime_start - datetime.timedelta(hours=8) , creationtime__lte = calculation_datetime_end).values_list('creationtime', 'substatus').order_by('creationtime'))
        fabricated_parts = list(ThingworxLocalsmartkpi.objects.filter(machine = machine, numberofparts__gte = 1, productiontime__gte = calculation_datetime_start, productiontime__lt = calculation_datetime_end ).values_list('ordernumber','productiontime','ispartok','numberofparts').order_by('productiontime'))
        i = calculation_datetime_start
        if interval == 4:
            while i < calculation_datetime_end:
                time_intervals[i] = []
                i += datetime.timedelta(hours=interval)
            for ordernumber, productiontime, ispartok, numberofparts in fabricated_parts:
                if ispartok == 1:
                    rounded_productiontime = productiontime.replace(second=0, microsecond=0, minute=0, hour = productiontime.hour // interval * 4)
                    if rounded_productiontime not in number_of_parts:
                        number_of_parts[rounded_productiontime] = []
                    number_of_parts[rounded_productiontime].append(numberofparts)
                    if rounded_productiontime not in orders:
                        orders[rounded_productiontime] = []
                    if ordernumber not in orders[rounded_productiontime]:
                        orders[rounded_productiontime].append(ordernumber)
            number_of_parts_sum = {k:sum(v) for k,v in number_of_parts.items()}
            for index, elem in enumerate(line_describtion):
                if (index+1 < len(line_describtion) and index - 1 >= 0):
                    end_time = line_describtion[index+1][0]
                    start_time = line_describtion[index][0]
                    substatus = line_describtion[index][1]
                    if substatus == 'KBMaschStatus.2.Productive.Start':
                        productive_times.append([start_time, end_time])
            for start_time, end_time in productive_times:
                rounded_start_time = start_time.replace(second=0, microsecond=0, minute=0, hour = start_time.hour // interval * 4)
                if end_time < (rounded_start_time + datetime.timedelta(hours=interval)):
                    timedelta = (end_time - start_time).total_seconds()
                    time_intervals[rounded_start_time].append(timedelta)
                else:
                    while rounded_start_time <= end_time:
                        if (start_time.replace(second=0, microsecond=0, minute=0, hour = start_time.hour // interval * 4)) == rounded_start_time:
                            timedelta = ((rounded_start_time + datetime.timedelta(hours=interval)) - start_time).total_seconds()
                        elif end_time > (rounded_start_time + datetime.timedelta(hours=interval)):
                            timedelta = interval * 60 * 60
                        else:
                            timedelta = (end_time - rounded_start_time).total_seconds()
                        time_intervals[rounded_start_time].append(timedelta)
                        rounded_start_time += datetime.timedelta(hours=interval)
            time_intervals_sum = {k:sum(v) for k,v in time_intervals.items()}
            for key in time_intervals_sum:
                machine = machine
                start_time = key
                end_time = key + datetime.timedelta(hours=interval)
                if number_of_parts_sum.get(key) is not None:
                    number_of_parts = number_of_parts_sum[key]
                else:
                    number_of_parts = 0
                if orders.get(key) is not None:
                    ordernumbers = orders[key]
                else:
                    ordernumbers = "-"
                lineprocessingtime = time_intervals_sum[key]
                if number_of_parts != 0:
                    if lineprocessingtime == 0:
                        dlp1 = -1
                    else:
                        time_of_one_piece = lineprocessingtime / number_of_parts
                        dlp1 = 3600 / time_of_one_piece
                else:
                    dlp1 = 0
                DLP14hrs.objects.update_or_create(machine=machine, time_start=start_time, time_end=end_time, defaults={'dlp1':dlp1, 'order':ordernumbers, 'lineprocessingtime':lineprocessingtime, 'numberofparts':number_of_parts})
        else:
            while i < calculation_datetime_end:
                time_intervals[i] = []
                i += datetime.timedelta(minutes=interval)
            for ordernumber, productiontime, ispartok, numberofparts in fabricated_parts:
                if ispartok == 1:
                    rounded_productiontime = productiontime.replace(second=0, microsecond=0, minute=(productiontime.minute // interval * 15), hour = productiontime.hour)
                    if rounded_productiontime not in number_of_parts:
                        number_of_parts[rounded_productiontime] = []
                    number_of_parts[rounded_productiontime].append(numberofparts)
                    if rounded_productiontime not in orders:
                        orders[rounded_productiontime] = []
                    if ordernumber not in orders[rounded_productiontime]:
                        orders[rounded_productiontime].append(ordernumber)
            number_of_parts_sum = {k:sum(v) for k,v in number_of_parts.items()}
            for index, elem in enumerate(line_describtion):
                if (index+1 < len(line_describtion) and index - 1 >= 0):
                    end_time = line_describtion[index+1][0]
                    start_time = line_describtion[index][0]
                    substatus = line_describtion[index][1]
                    if substatus == 'KBMaschStatus.2.Productive.Start':
                        productive_times.append([start_time, end_time])
            for start_time, end_time in productive_times:
                rounded_start_time = start_time.replace(second=0, microsecond=0, minute=(start_time.minute // interval * 15), hour = start_time.hour)
                if end_time < (rounded_start_time + datetime.timedelta(minutes=interval)):
                    timedelta = (end_time - start_time).total_seconds()
                    time_intervals[rounded_start_time].append(timedelta)
                else:
                    while rounded_start_time <= end_time:
                        if (start_time.replace(second=0, microsecond=0, minute=(start_time.minute // interval * 15), hour = start_time.hour)) == rounded_start_time:
                            timedelta = ((rounded_start_time + datetime.timedelta(minutes=interval)) - start_time).total_seconds()
                        elif end_time > (rounded_start_time + datetime.timedelta(minutes=interval)):
                            timedelta = interval * 60
                        else:
                            timedelta = (end_time - rounded_start_time).total_seconds()
                        time_intervals[rounded_start_time].append(timedelta)
                        rounded_start_time += datetime.timedelta(minutes=interval)
            time_intervals_sum = {k:sum(v) for k,v in time_intervals.items()}
            for key in time_intervals_sum:
                machine = machine
                start_time = key
                end_time = key + datetime.timedelta(minutes=interval)
                if number_of_parts_sum.get(key) is not None:
                    number_of_parts = number_of_parts_sum[key]
                else:
                    number_of_parts = 0
                if orders.get(key) is not None:
                    ordernumbers = orders[key]
                else:
                    ordernumbers = "-"
                lineprocessingtime = time_intervals_sum[key]
                if number_of_parts != 0:
                    if lineprocessingtime == 0:
                        dlp1 = -1
                    else:
                        time_of_one_piece = lineprocessingtime / number_of_parts
                        dlp1 = 3600 / time_of_one_piece
                else:
                    dlp1 = 0
                if interval == 15:
                    DLP115min.objects.update_or_create(machine=machine, time_start=start_time, time_end=end_time, defaults={'dlp1':dlp1, 'order':ordernumbers, 'lineprocessingtime':lineprocessingtime, 'numberofparts':number_of_parts})
                elif interval == 60:
                    DLP160min.objects.update_or_create(machine=machine, time_start=start_time, time_end=end_time, defaults={'dlp1':dlp1, 'order':ordernumbers, 'lineprocessingtime':lineprocessingtime, 'numberofparts':number_of_parts})

    return HttpResponse("OK")

