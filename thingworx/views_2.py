from .models import Smartkpivalues, FP09_oee_manual_entries
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models.functions import Trunc
from django.db.models import F

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

        our_oee = list(Smartkpivalues.objects.filter(kpidatetime__gte=range_from, kpidatetime__lt=range_to, kpiname='CVS: OEE (Version 2)', machine='KBLIBFP09-Lanico2MachineThing', kpitimebase='shift').exclude(kpidatetime__in=list_of_excluded_shifts).annotate(adjusted_day=F('kpidatetime') + datetime.timedelta(hours=2)).annotate(day=Trunc('adjusted_day', 'day')).values_list('adjusted_day', 'kpifloatvalue'))

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
            'labels': [str(k.date()) for k, v in calculated_days.items()],
            'values': [v['average'] for k, v in calculated_days.items()],
            'days': data['days'],
        }

    else:

        twx_oee = list(Smartkpivalues.objects.filter(kpidatetime__gte=range_to, kpidatetime__lt=range_from, kpiname='CVS: OEE (Version 2)', machine='KBLIBFP09-Lanico2MachineThing', kpitimebase='day').exclude(kpifloatvalue=0.0).values_list('kpidatetime', 'kpifloatvalue'))

        labels = [str(dt.date()) for (dt, value) in twx_oee]
        values = [value for (dt, value) in twx_oee]

        return_data = {
            'labels': list(labels),
            'values': list(values),
            'days': data['days'],
        }

    return JsonResponse(return_data)

