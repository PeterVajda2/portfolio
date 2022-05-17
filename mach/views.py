from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import DowntimeFromLine, Station, Downtime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Sum, When, Case, Value, CharField, DateTimeField, ExpressionWrapper, Func
from django.db.models.functions import ExtractHour, Trunc, Extract
import json
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict



# Create your views here.


@csrf_exempt
def mach_operator_screen(request, station):
    if request.method == "GET":
        categories = Downtime.objects.distinct('category').values('category', 'color')
        downtimes = Downtime.objects.values('category', 'downtime')
        # downtimes_from_station = list(DowntimeFromLine.objects.filter(station = Station.objects.get(name = station), beginning_t__gte = datetime.datetime.now() - datetime.timedelta(days = 1)).annotate(beginning_as_str=Cast('beginning_t', TextField())).annotate(end_as_str=Cast('end_t', TextField())).values('downtime__category', 'downtime__downtime', 'beginning_as_str', 'end_as_str'))

        context = {
            'categories': categories,
            'data': json.dumps(query_to_dict(downtimes), ensure_ascii=False),
            'station': station,
            # 'downtime_from_station': downtimes_from_station,
        }

        return render(request, 'mach_operator.html', context)

    if request.method == "POST":
        body = json.loads(request.body)

        if body['action'] == 'POST':
            category = body['category']
            downtime = body['downtime']
            start = body['start']
            adjusted_start = start[:16] + ":00.000Z"
            id = body['id']
            try:
                currently_active_downtime = DowntimeFromLine.objects.get(end_t__isnull=True)
                currently_active_downtime.end_t = adjusted_start
                currently_active_downtime.save()
                DowntimeFromLine.objects.update_or_create(uid = id, defaults={'downtime': Downtime.objects.get(category = category, downtime = downtime), 'beginning_t': adjusted_start, 'station': Station.objects.get(name = station)})
            except:
                DowntimeFromLine.objects.update_or_create(uid = id, defaults={'downtime': Downtime.objects.get(category = category, downtime = downtime), 'beginning_t': adjusted_start, 'station': Station.objects.get(name = station)})


        if body['action'] == 'GET':
            if datetime.datetime.now().hour < 12:
                since = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0, 0)) - datetime.timedelta(hours = 12 * body['steps_back'])
            else:
                since = datetime.datetime.combine(datetime.date.today(), datetime.time(12, 0, 0, 0)) - datetime.timedelta(hours = 12 * body['steps_back'])

            return JsonResponse({'result': list(DowntimeFromLine.objects.filter(station = Station.objects.get(name = station), beginning_t__gte = since).values_list('downtime__category', 'downtime__downtime', 'downtime__color', 'beginning_t', 'end_t', 'uid', 'comment'))})


        if body['action'] == 'COMMENT':
            DowntimeFromLine.objects.filter(uid = body['id']).update(comment = body['comment'])

        if body['action'] == 'FETCH ONE':
            return JsonResponse(json.dumps(model_to_dict(DowntimeFromLine.objects.get(uid = body['id'])), cls=DjangoJSONEncoder), safe=False)

        if body['action'] == 'INCREASE':
            if body['boundary'] == 'end':
                downtime = DowntimeFromLine.objects.get(uid = body['id'])
                increase_in_minutes = 1 if body['unit'] == 'minute' else 60
                next_downtime = DowntimeFromLine.objects.filter(beginning_t=downtime.end_t, station=downtime.station).first()
                downtime.end_t = downtime.end_t + datetime.timedelta(minutes = increase_in_minutes)
                downtime.save()
                next_downtime.beginning_t = next_downtime.beginning_t + datetime.timedelta(minutes = increase_in_minutes)
                if next_downtime.end_t and next_downtime.beginning_t >= next_downtime.end_t:
                    next_downtime.delete()
                else:
                    next_downtime.save()
                return JsonResponse([model_to_dict(downtime), model_to_dict(next_downtime)], safe=False, encoder=DjangoJSONEncoder, json_dumps_params={'ensure_ascii': False})

            if body['boundary'] == 'beginning':
                downtime = DowntimeFromLine.objects.get(uid = body['id'])
                increase_in_minutes = 1 if body['unit'] == 'minute' else 60
                previous_downtime = DowntimeFromLine.objects.filter(end_t=downtime.beginning_t, station=downtime.station).first()
                downtime.beginning_t = downtime.beginning_t + datetime.timedelta(minutes = increase_in_minutes)
                downtime.save()
                if previous_downtime:
                    previous_downtime.end_t = previous_downtime.end_t + datetime.timedelta(minutes = increase_in_minutes)
                    if previous_downtime.end_t > previous_downtime.beginning_t:
                        previous_downtime.save()
                    return JsonResponse([model_to_dict(downtime), model_to_dict(previous_downtime)], safe=False, encoder=DjangoJSONEncoder, json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse([model_to_dict(downtime), model_to_dict(downtime)], safe=False, encoder=DjangoJSONEncoder, json_dumps_params={'ensure_ascii': False})

        if body['action'] == 'DECREASE':
            if body['boundary'] == 'end':
                downtime = DowntimeFromLine.objects.get(uid = body['id'])
                decrease_in_minutes = 1 if body['unit'] == 'minute' else 60
                next_downtime = DowntimeFromLine.objects.filter(beginning_t=downtime.end_t, station=downtime.station).first()
                downtime.end_t = downtime.end_t - datetime.timedelta(minutes = decrease_in_minutes)
                if downtime.end_t > downtime.beginning_t:
                    downtime.save()
                    next_downtime.beginning_t = next_downtime.beginning_t - datetime.timedelta(minutes = decrease_in_minutes)
                    next_downtime.save()
                return JsonResponse([model_to_dict(downtime), model_to_dict(next_downtime)], safe=False, encoder=DjangoJSONEncoder, json_dumps_params={'ensure_ascii': False})

            if body['boundary'] == 'beginning':
                downtime = DowntimeFromLine.objects.get(uid = body['id'])
                decrease_in_minutes = 1 if body['unit'] == 'minute' else 60
                previous_downtime = DowntimeFromLine.objects.filter(end_t=downtime.beginning_t, station=downtime.station).first()
                downtime.beginning_t = downtime.beginning_t - datetime.timedelta(minutes = decrease_in_minutes)
                if previous_downtime:
                    previous_downtime.end_t = previous_downtime.end_t - datetime.timedelta(minutes = decrease_in_minutes)
                    if previous_downtime.end_t > previous_downtime.beginning_t:
                        downtime.save()
                        previous_downtime.save()
                    return JsonResponse([model_to_dict(downtime), model_to_dict(previous_downtime)], safe=False, encoder=DjangoJSONEncoder, json_dumps_params={'ensure_ascii': False})

                else:
                    downtime.save()
                    return JsonResponse([model_to_dict(downtime), model_to_dict(downtime)], safe=False, encoder=DjangoJSONEncoder, json_dumps_params={'ensure_ascii': False})



        return JsonResponse({'result': 'okay'})


def split_downtimes(request):
    downtimes_ended_in_last_day = DowntimeFromLine.objects.filter(beginning_t__gte=datetime.datetime.today() - datetime.timedelta(days = 1))

    for downtime in downtimes_ended_in_last_day:
        if downtime.end_t:
            if downtime.beginning_t.hour < 12 and (downtime.end_t.hour > 12 or downtime.end_t.day > downtime.beginning_t.day):
                original_end_t = downtime.end_t
                downtime.end_t = datetime.datetime.combine(downtime.beginning_t.date(), datetime.time(12, 0, 0, 0))
                downtime.save()

                downtime.pk = None
                downtime._state.adding = True
                downtime.beginning_t = datetime.datetime.combine(downtime.beginning_t.date(), datetime.time(12, 0, 0, 0))
                downtime.uid = int(downtime.beginning_t.timestamp())
                downtime.end_t = original_end_t
                downtime.save()

            if downtime.beginning_t.hour > 23 and downtime.end_t.hour < 1:
                original_end_t = downtime.end_t
                downtime.end_t = datetime.datetime.combine(downtime.beginning_t.date() + datetime.timedelta(days=1), datetime.time(0, 0, 0, 0))
                downtime.save()

                downtime.pk = None
                downtime._state.adding = True
                downtime.beginning_t = datetime.datetime.combine(downtime.beginning_t.date() + datetime.timedelta(days=1), datetime.time(0, 0, 0, 0))
                downtime.uid = int(downtime.beginning_t.timestamp())
                downtime.end_t = original_end_t
                downtime.save()

        if not downtime.end_t:
            if downtime.beginning_t.hour < 12 and datetime.datetime.now().hour >= 12:
                downtime.end_t = datetime.datetime.combine(downtime.beginning_t.date(), datetime.time(12, 0, 0, 0))
                downtime.save()

                downtime.pk = None
                downtime._state.adding = True
                downtime.beginning_t = datetime.datetime.combine(downtime.beginning_t.date(), datetime.time(12, 0, 0, 0))
                downtime.uid = int(downtime.beginning_t.timestamp())
                downtime.end_t = None
                downtime.save()

            if downtime.beginning_t.hour > 23 and datetime.datetime.now().hour >= 0:
                downtime.end_t = datetime.datetime.combine(downtime.beginning_t.date() + datetime.timedelta(days=1), datetime.time(0, 0, 0, 0))
                downtime.save()

                downtime.pk = None
                downtime._state.adding = True
                downtime.beginning_t = datetime.datetime.combine(downtime.beginning_t.date() + datetime.timedelta(days=1), datetime.time(0, 0, 0, 0))
                downtime.uid = int(downtime.beginning_t.timestamp())
                downtime.save()

            if downtime.beginning_t.day < datetime.datetime.today().day:
                downtime.end_t = datetime.datetime.combine(downtime.beginning_t.date() + datetime.timedelta(days=1), datetime.time(0, 0, 0, 0))
                downtime.save()

                downtime.pk = None
                downtime._state.adding = True
                downtime.beginning_t = datetime.datetime.combine(downtime.beginning_t.date() + datetime.timedelta(days=1), datetime.time(0, 0, 0, 0))
                downtime.uid = int(downtime.beginning_t.timestamp())
                downtime.end_t = None
                downtime.save()


    return HttpResponse('okay')


def query_to_dict(query):

    data = {}

    for tup in query:
        if not tup['category'] in data:
            data[tup['category']] = [tup['downtime']]
        else:
            data[tup['category']].append(tup['downtime'])
            
    return data


def split_downtimes():
    downtimes_ended_in_last_day = DowntimeFromLine.objects.filter(beginning_t__gte=datetime.datetime.now() - datetime.timedelta(days=1))

    for downtime in downtimes_ended_in_last_day:
        downtime_shift_end = get_shift_end(downtime)
        if (downtime.end_t and downtime.end_t > downtime_shift_end) or (not downtime.end_t and datetime.datetime.now() > downtime_shift_end):
            original_downtime_end = downtime.end_t
            downtime.end_t = downtime_shift_end
            downtime.save()

            new_downtime = DowntimeFromLine.objects.create(
                station = downtime.station,
                downtime = downtime.downtime,
                beginning_t = downtime_shift_end,
                end_t = original_downtime_end,
                comment = downtime.comment,
                uid = downtime.uid + 1,
            )


def get_shift_end(downtime):
    if 6 <= downtime.beginning_t.hour < 14:
        return downtime.beginning_t.replace(hour=14, minute=0, second=0)
    if 14 <= downtime.beginning_t.hour < 22:
        return downtime.beginning_t.replace(hour=22, minute=0, second=0)
    if downtime.beginning_t.hour >= 22:
        try:
            return downtime.beginning_t.replace(day=downtime.beginning_t.day + 1, hour=6, minute=0, second=0)
        except ValueError:
            if downtime.beginning_t.month < 12:
                return downtime.beginning_t.replace(day=1, month=downtime.beginning_t.month + 1, hour=6, minute=0, second=0)
            else:
                return downtime.beginning_t.replace(day=1, month=1, year=downtime.beginning_t.year + 1, hour=6, minute=0, second=0)
    if downtime.beginning_t.hour < 6:
        return downtime.beginning_t.replace(hour=6, minute=0, second=0)


def show_reports(request):
    morning_shift_hours = [6, 7, 8, 9, 10, 11, 12, 13]
    afternoon_shift_hours = [14, 15, 16, 17, 18, 19, 20, 21]
    shifts = ['Morning', 'Afternoon', 'Night']

    split_downtimes()

    if request.method == "POST":
        request_data = json.loads(request.body) if request.body else {'beginning': datetime.date.today(), 'end': datetime.date.today() + datetime.timedelta(days=1)}

        beginning = request_data['beginning']
        end = request_data['end']
        stations = Station.objects.filter(name__in=request_data['station']) if 'station' in request_data else Station.objects.get(name='OC25A')

        downtimes = list(DowntimeFromLine.objects.filter(beginning_t__gte=beginning, end_t__lte=end, station__in=stations).annotate(hour_start=ExtractHour('beginning_t')).annotate(shift=Case(When(hour_start__in=morning_shift_hours, then=Value('Morning')), When(hour_start__in=afternoon_shift_hours, then=Value('Afternoon')), default=Value('Night'), output_field=CharField())).annotate(duration=F("end_t") - F("beginning_t")).filter(shift__in=shifts).annotate(beginning_offset=ExpressionWrapper(F("beginning_t") + datetime.timedelta(hours=2), output_field=DateTimeField())).annotate(day=Trunc('beginning_offset', 'day')).values('station__name', 'downtime__category', 'day', 'shift').annotate(total_duration=Sum('duration')).values('station__name', 'downtime__category', 'total_duration', 'day', 'shift').annotate(days=Extract('total_duration', 'day'), hours=Extract('total_duration', 'hour'), minutes=Extract('total_duration', 'minute'), seconds=Extract('total_duration', 'second')).annotate(formatted_date=Func(F('day'), Value('yyyy-MM-dd'), function='to_char', output_field=CharField())).annotate(duration_seconds=F('days') * 86400 + F('hours') * 3600 + F('minutes') * 60 + F('seconds')).values('station__name', 'downtime__category', 'formatted_date', 'shift', 'duration_seconds'))

        return JsonResponse({'data': downtimes}, json_dumps_params={'ensure_ascii': False})

    if request.method == "GET":
        downtimes = list(DowntimeFromLine.objects.filter(beginning_t__gte=datetime.datetime.now() - datetime.timedelta(days=1), end_t__isnull=False, station=Station.objects.get(name='OC25A')).annotate(hour_start=ExtractHour('beginning_t')).annotate(shift=Case(When(hour_start__in=morning_shift_hours, then=Value('Morning')), When(hour_start__in=afternoon_shift_hours, then=Value('Afternoon')), default=Value('Night'), output_field=CharField())).annotate(duration=F("end_t") - F("beginning_t")).filter(shift__in=shifts).annotate(beginning_offset=ExpressionWrapper(F("beginning_t") + datetime.timedelta(hours=2), output_field=DateTimeField())).annotate(day=Trunc('beginning_offset', 'day')).values('station__name', 'downtime__category', 'day', 'shift').annotate(total_duration=Sum('duration')).values('station__name', 'downtime__category', 'total_duration', 'day', 'shift').annotate(days=Extract('total_duration', 'day'), hours=Extract('total_duration', 'hour'), minutes=Extract('total_duration', 'minute'), seconds=Extract('total_duration', 'second')).annotate(formatted_date=Func(F('day'), Value('yyyy-MM-dd'), function='to_char', output_field=CharField())).annotate(duration_seconds=F('days') * 86400 + F('hours') * 3600 + F('minutes') * 60 + F('seconds')).values('station__name', 'downtime__category', 'formatted_date', 'shift', 'duration_seconds'))

        return render(request, 'mach_reports.html', {'data': downtimes})