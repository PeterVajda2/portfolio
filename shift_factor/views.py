from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from Knorr.settings import TEMPORARY_IMAGES_ROOT
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import OBC_Linka1, Productioncounts, RobotSchedule
from thingworx.models import Smartkpiorderkeyvaluedata
import json
import datetime
import statistics


def shift_factor(request):
    machine = request.GET.get('machine', '')
    hours_delta = 11
    now = datetime.datetime.now() - datetime.timedelta(hours=hours_delta)
    hrfromnow = now - datetime.timedelta(hours=1)
    if machine == 'OBC-1':
        if now.strftime("%H:%M:%S")[0:2] == "00":
            productiontimes = list(OBC_Linka1.objects.filter(datum__in=[now.date(), now.date()-datetime.timedelta(day=1)]).order_by('datum', 'cas').values_list('cas', 'datum', 'zakazka'))
        else:
            productiontimes = list(OBC_Linka1.objects.filter(datum=now.date()).order_by('datum', 'cas').values_list('cas', 'datum', 'zakazka'))
    ordernumber_productiontimes = []
    for time, date, ordernumber in productiontimes:
        productiontime = datetime.datetime.combine(date.date(), time.time())
        if productiontime > hrfromnow and productiontime < now:
            ordernumber_productiontimes.append([productiontime, ordernumber])
    ordernumbers_dictionary = {}
    for count, value in enumerate(ordernumber_productiontimes):
        if count == 0:
            time_start = ordernumber_productiontimes[count][0]
        else:
            production_start = ordernumber_productiontimes[count-1][0]
            production_end = ordernumber_productiontimes[count][0]
            ordernumber = ordernumber_productiontimes[count][1]
            production_time = int((production_end - production_start).total_seconds())
            if ordernumber not in ordernumbers_dictionary:
                ordernumbers_dictionary[ordernumber] = []
            ordernumbers_dictionary[ordernumber].append(production_time)
    list_of_SAPAPO = []
    list_of_production_times = []
    nothing = 0
    for key in ordernumbers_dictionary:
        print(key)
        SAPAPO = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber=key, propertykey='ProcessingTimeAPO-0010').values_list('floatvalue', 'textvalue'))
        #SAPAPO = [2, "MIN"]
        if len(SAPAPO) == 0:
            break
        else:
            if SAPAPO[1] == "MIN":
                SAPAPO[0] = SAPAPO[0]*60
                SAPAPO[1] = "SEC"
            times = ordernumbers_dictionary[key]
            for time in times:
                nothing = 1
                list_of_SAPAPO.append(SAPAPO[0])
                list_of_production_times.append(time)
    
    if nothing == 0:
        shift_factor_coef = "Neznam SAP APO"
    else:
        shift_factor_coef = round(sum(list_of_production_times) / sum(list_of_SAPAPO),2)

    context = { 'machine': machine,
                'shift_factor': shift_factor_coef}
    return render(request, 'shift_factor.html', context)

@csrf_exempt
def apo_comparison(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        machine_change = request_data['machine_change']

        if machine_change == 1:
            machine = request_data['machine']
            partnumbers = get_partnumbers(machine)
            return_data = {'partnumbers': partnumbers}
            return JsonResponse(return_data)

        if machine_change == 0:
            machine = request_data['machine']
            if machine == 'OBC-1':
                partnumber = request_data['partnumber']
                data_percentage = request_data['data_percentage']
                ordernumbers = get_ordernumbers(machine, partnumber)
                productiontimes = get_productiontimes(machine, partnumber)
                TgMax, SAPAPO = get_SAPAPO_and_TgMax(ordernumbers)
                production = get_production_times(productiontimes)
                ProductiveTimesWithoutExtreme = filter_extremes(production, data_percentage)
                numberofpartsininterval, intervals = fit_data_in_intervals(ProductiveTimesWithoutExtreme)
            
                MeanOfProductiveTimesWithoutExtreme = round(statistics.mean(ProductiveTimesWithoutExtreme),2)
                MeanOfProductiveTimes = round(statistics.mean(production),2)
                MedianOfProductiveTimesWithoutExtreme = round(statistics.median(ProductiveTimesWithoutExtreme),2)
                MedianOfProductiveTimes = round(statistics.median(production), 2)

                return_data = { 'intervals': intervals,
                                'numberofpartsininterval': numberofpartsininterval,
                                'partnumber': partnumber,
                                'numberofpartsdisplayed': len(ProductiveTimesWithoutExtreme),
                                'numberofpartssum': len(production),
                                'meanofproductivetimes': MeanOfProductiveTimes,
                                'meanofproductivetimeswithoutextreme': MeanOfProductiveTimesWithoutExtreme,
                                'tgmax': TgMax[0],
                                'sapapo': SAPAPO[0],
                                'medianofproductivetimes': MedianOfProductiveTimes,
                                'medianofproductivetimeswithoutextreme': MedianOfProductiveTimesWithoutExtreme,
                                'timeunit': SAPAPO[1],
                                'productivetimes': production,
                                'timeunitTgMax': TgMax[1],
                                }
                return JsonResponse(return_data)
        else:
            productiontimes = request_data['productivetimes']
            sapapoperc = float(request_data['sap_apo_perc'])
            sapapopercint = int(sapapoperc) - 1
            DataPercentage = statistics.quantiles(productiontimes, n=101)
            sapapotime = DataPercentage[sapapopercint]
            return_data = {'sapapotime': sapapotime}
        return JsonResponse(return_data)


    if request.method == "GET":
        machines = ['OBC-1']
        context = {
            'machines': machines
        }
        return render(request, 'apo_comparison.html', context)



def get_partnumbers(machine):
    if machine == 'OBC-1':
        partnumbers = list(OBC_Linka1.objects.all().values_list('vcislo', flat=True).distinct())
    return partnumbers

def get_ordernumbers(machine, partnumber):
    if machine == 'OBC-1':
        ordernumbers = list(OBC_Linka1.objects.filter(vcislo=partnumber).values_list('zakazka', flat=True).distinct())
    return ordernumbers

def get_productiontimes(machine, partnumber):
    if machine == 'OBC-1':
        production_times = list(OBC_Linka1.objects.filter(vcislo=partnumber).order_by('datum', 'cas').values_list('datum', 'cas'))
    return production_times

def  get_SAPAPO_and_TgMax(ordernumbers):
    TgMax = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=ordernumbers, propertykey='tgMaxTime-0010').values_list('floatvalue', 'textvalue').last())
    SAPAPO = list(Smartkpiorderkeyvaluedata.objects.filter(ordernumber__in=ordernumbers, propertykey='ProcessingTimeAPO-0010').values_list('floatvalue', 'textvalue').last())
    if SAPAPO[1] == "MIN":
        SAPAPO[0] = SAPAPO[0]*60
        SAPAPO[1] = "SEC"
    if TgMax[1] == "MIN":
        TgMax[0] = TgMax[0]*60
        TgMax[1] = "SEC"
    return TgMax, SAPAPO

def get_production_times(productiontimes):
    productiontimes_list = []
    for date, time in productiontimes:
        productiontime = datetime.datetime.combine(date.date(), time.time())
        productiontimes_list.append(productiontime)
    production = []
    for count, value in enumerate(productiontimes_list):
        if count == 0:
            pass
        else:
            production_start = productiontimes_list[count-1]
            production_end = productiontimes_list[count]
            production_time = int((production_end - production_start).total_seconds())
            if production_start < production_end:
                production.append(production_time)
    return production

def filter_extremes(production, data_percentage):
    DataPercentage = statistics.quantiles(production, n=101)
    PercentageOfData = int(data_percentage)
    i = int((100 - PercentageOfData) / 2)
    if i == 0:
        ProductiveTimesWithoutExtreme = production
    else:
        SmallerPercentage = DataPercentage[i]
        BiggerPercentage = DataPercentage[100-i]
        ProductiveTimesWithoutExtreme = []
        for productivetime in production:
            if productivetime > BiggerPercentage or productivetime < SmallerPercentage:
                continue
            else:
                ProductiveTimesWithoutExtreme.append(productivetime)
    return ProductiveTimesWithoutExtreme

def fit_data_in_intervals(ProductiveTimesWithoutExtreme):
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
        for productivetime in ProductiveTimesWithoutExtreme:
            if productivetime >= Start and productivetime < End:
                partsininterval += 1
        numberofpartsininterval.append(partsininterval)
    return numberofpartsininterval, intervals


def get_data_jirkal(request):

    return HttpResponse('zatim nevim')


@csrf_exempt
def sap_robot(request):
    current_robot_data = RobotSchedule.objects.filter(order_closed=False)

    for order in current_robot_data:
        if order.target_quantity == order.current_sap_quantity:
            order.order_closed = True
        if not Productioncounts.objects.filter(ordernumber=order.order_number).exists():
            order.order_closed = True

    context = {
        'current_robot_data': RobotSchedule.objects.filter(order_closed=False),
    }

    if request.method == "POST":
        if 'delete' in request.POST:
            RobotSchedule.objects.filter(order_number=request.POST.get('order-number')).delete()
        else:
            data, created = RobotSchedule.objects.update_or_create(order_number = request.POST.get('order-number'), defaults={'group_id': request.POST.get('group-id'), 'sap_max': request.POST.get('max-quantity')})

    return render(request, 'sap_robot.html', context)


def update_robot_data(request):
    orders_for_robot = RobotSchedule.objects.filter(order_closed=False)
    data_from_sql = list(Productioncounts.objects.values_list('ordernumber', 'typenumber', 'orderpcs', 'okpcs', 'timeoflastupdate'))
    data_dict = {}

    for item in data_from_sql:
        order_number = item[0]
        data_dict[order_number] = {}
        data_dict[order_number]['type_number'] = item[1]
        data_dict[order_number]['target_quantity'] = item[2]
        data_dict[order_number]['sql_quantity'] = item[3]
        data_dict[order_number]['last_update_sql'] = item[4]

    for order in orders_for_robot:
        try:
            if order.current_sap_quantity == order.target_quantity and order.current_sap_quantity > 0:
                order.order_closed = True
                order.save()
            else:
                order.target_quantity = data_dict[order.order_number]['target_quantity']
                order.type_number = data_dict[order.order_number]['type_number']
                order.current_sql_quantity = data_dict[order.order_number]['sql_quantity']
                order.sql_update_time = data_dict[order.order_number]['last_update_sql']
                if order.sap_max == 0:
                    order.sap_max = order.target_quantity
                order.save()
        except:
            pass

    return HttpResponse('okay')


