from django.forms import TimeField
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from logistics.models import EmailNotification, Shift, Subcategory, TrainCircuit, Line, Downtime, ProductionArea, Profile, Category, TrainDriver
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
from fp09.models import DowntimeFromLine 
from django.db.models import F, Sum, Count, IntegerField
import random
import operator
from django.contrib.auth.decorators import login_required
from openpyxl import load_workbook
from django.template.loader import render_to_string 
from django.core.mail import EmailMessage
from django.db.models import F, Sum, DateTimeField
import re
from django.db.models.functions import Cast, Trunc
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile



def upload_excel(request):
    if request.method == 'POST':
        my_uploaded_file = request.FILES['file']
        workbook = load_workbook(my_uploaded_file)
        sheet = workbook.active
        rows = sheet.rows
        headers = [cell.value for cell in next(rows)]
        headers = [cell.value for cell in next(rows)]
        headers = [cell.value for cell in next(rows)]
        all_rows = []
        headers_number = []
        for i in range(len(headers)):
            headers_number.append(i)

        for row in rows:
            data = {}
            for title, cell in zip(headers_number, row):
                data[title] = cell.value
            all_rows.append(data)

        switch = 0
        if switch == 1:
            for one_record in all_rows:
                ProductionAreaPost = one_record[0]
                ProductionAreaObject = ProductionArea.objects.filter(name = ProductionAreaPost).first()
                Date = one_record[3].date()
                Shift = one_record[6]
                Noticed = one_record[7]
                LinePost = one_record[9]
                LineObject = Line.objects.filter(name=LinePost).first()
                TrainCircuitPost = int(one_record[8])
                TrainCircuitPostObject = TrainCircuit.objects.filter(number = TrainCircuitPost, line = LineObject).first()
                Ordernumber = one_record[10]
                MaterialNumber = one_record[11]
                DowntimePost = True if one_record[12] == 'Ano' or 'ano' or 'ANo' or 'ANO' or 'aNO' or 'anO' else False
                TimeFrom = one_record[13]
                TimeTo = one_record[14]
                TrainDriverPost = one_record[16]
                TrainDriverObject = TrainDriver.objects.filter(train_driver = TrainDriverPost).first()
                CategoryPost = one_record[17]
                CategoryObject = Category.objects.filter(category = CategoryPost).first()
                SpecificationPost = one_record[18]
                SubcategoryObject = Subcategory.objects.filter(subcategory = SpecificationPost).first()
                Notes = one_record[19]
                CategoryByLogistic = Category.objects.filter(category = one_record[21]).first()
                SpecificationByLogistic = Subcategory.objects.filter(subcategory = one_record[22]).first()
                NotesByLogistic = one_record[23]
                DowntimePostByLogistic = True 

                Downtime.objects.create(
                production_area = ProductionAreaObject,
                downtime_date = Date,
                shift = Shift,
                recorded_by = Noticed,
                train_circuit = TrainCircuitPostObject, 
                line_id = LinePost, 
                order_number = Ordernumber, 
                material_number = MaterialNumber,
                is_downtime_by_production = DowntimePost,
                downtime_start = TimeFrom, 
                downtime_end = TimeTo, 
                train_driver = TrainDriverObject, 
                category_by_production = CategoryObject, 
                subcategory_by_production = SubcategoryObject,
                note_by_production = Notes,
                category_by_logistics = CategoryByLogistic,
                subcategory_by_logistics = SpecificationByLogistic,
                note_by_logistics = NotesByLogistic,
                is_downtime_by_logistics = DowntimePostByLogistic)
        else:
            for one_record in all_rows:
                ProductionAreaPost = one_record[0]
                ProductionAreaObject = ProductionArea.objects.filter(name = ProductionAreaPost).first()
                try:
                    Date = one_record[3].date()
                except:
                    Date = datetime.datetime(2000, 1, 1)
                Shift = one_record[6]
                Noticed = one_record[7]
                LinePost = one_record[9]
                LineObject = Line.objects.filter(name=LinePost).first()
                Ordernumber = one_record[10]
                MaterialNumber = one_record[11]
                DowntimePost = True if one_record[12] == 'Ano' or 'ano' or 'ANo' or 'ANO' or 'aNO' or 'anO' else False
                try:
                    TimeFromTime = one_record[13]
                    TimeFrom = datetime.datetime.combine(Date, TimeFromTime)
                    if one_record[13] < one_record[14]:
                        TimeToTime = one_record[14]
                        TimeTo = datetime.datetime.combine(Date, TimeToTime)
                    else:
                        TimeToTime = one_record[14]
                        DatePlusDay = Date + datetime.timedelta(days = 1)
                        TimeTo = datetime.datetime.combine(DatePlusDay, TimeToTime)
                except:
                    pass
                CategoryPost = one_record[17]
                CategoryObject = Category.objects.filter(category = CategoryPost).first()
                if CategoryObject == None:
                    try:
                        if one_record[17] != None:
                            Category.objects.create(category = one_record[17])
                        else:
                            CategoryPost = '-'
                            Category.objects.create(category = CategoryPost)
                    except:
                        pass
                    CategoryObject = Category.objects.filter(category = CategoryPost).first()
                    CategoryInt = Category.objects.filter(category = CategoryPost).values('id').first()['id']
                SpecificationPost = one_record[18]
                SubcategoryObject = Subcategory.objects.filter(subcategory = SpecificationPost).first()
                if SubcategoryObject == None:
                    try:
                        if one_record[18] != None:
                            Subcategory.objects.create(subcategory = SpecificationPost, category_id = CategoryInt)
                        else:
                            SpecificationPost = '-'
                            Subcategory.objects.create(subcategory = SpecificationPost, category_id = CategoryInt)
                    except:
                        pass
                    SubcategoryObject = Subcategory.objects.filter(subcategory = SpecificationPost).first()
                Notes = one_record[19]
                CategoryPostByLogistic = one_record[21]
                print(CategoryPostByLogistic)
                CategoryByLogistic = Category.objects.filter(category = CategoryPostByLogistic).first()
                if CategoryByLogistic == None:
                    try:
                        if one_record[21] != None:
                            Category.objects.create(category = one_record[21])
                        else:
                            CategoryPostByLogistic = '-'
                            Category.objects.create(category = CategoryPostByLogistic)
                    except:
                        pass
                    CategoryByLogistic = Category.objects.filter(category = CategoryPostByLogistic).first()
                SubcategoryPostByLogistic = one_record[22]
                SpecificationByLogistic = Subcategory.objects.filter(subcategory = one_record[22]).first()
                CategoryIntLogistic = Category.objects.filter(category = CategoryPost).values('id').first()['id']
                print(CategoryPostByLogistic)
                if SpecificationByLogistic == None:
                    try:
                        if one_record[22] != None:
                            Subcategory.objects.create(subcategory = one_record[22], category_id = CategoryIntLogistic)
                        else:
                            SubcategoryPostByLogistic = '-'
                            Subcategory.objects.create(subcategory = SubcategoryPostByLogistic, category_id = CategoryIntLogistic)
                    except:
                        pass
                    SpecificationByLogistic = Subcategory.objects.filter(subcategory = SubcategoryPostByLogistic).first()
                NotesByLogistic = one_record[23]
                DowntimePostByLogistic = True
                print(one_record[18], one_record[22], one_record[17], one_record[21])
                print(SubcategoryObject, SpecificationByLogistic, CategoryObject, CategoryByLogistic)
                try:
                    Downtime.objects.create(
                    production_area = ProductionAreaObject,
                    downtime_date = Date,
                    shift = Shift,
                    recorded_by = Noticed,
                    line_id = LinePost, 
                    order_number = Ordernumber, 
                    material_number = MaterialNumber,
                    is_downtime_by_production = DowntimePost,
                    downtime_start = TimeFrom, 
                    downtime_end = TimeTo, 
                    category_by_production = CategoryObject, 
                    subcategory_by_production = SubcategoryObject,
                    note_by_production = Notes,
                    category_by_logistics = CategoryByLogistic,
                    subcategory_by_logistics = SpecificationByLogistic,
                    note_by_logistics = NotesByLogistic,
                    is_downtime_by_logistics = DowntimePostByLogistic)
                except:
                    pass

        return redirect('logistics:show_downtimes')
    if request.method == "GET":
        return render(request, 'upload_excel.html', {})

def index(request):

    return render(request, 'logistics_index.html', {})

@csrf_exempt
def visualization(request):

    if request.method == "POST":
        request_data = json.loads(request.body)
        DateFrom = datetime.datetime.strptime(request_data['DateFrom'], "%Y-%m-%d")
        DateTo = datetime.datetime.strptime(request_data['DateTo'], "%Y-%m-%d")
        button = request_data['button_option']
        days_in_range = []
        days = 0
        datetime_iteration = DateFrom
        while datetime_iteration.date() <= DateTo.date():
            days_in_range.append(datetime_iteration.date())
            datetime_iteration = datetime_iteration + datetime.timedelta(days=1)
            days += 1
        return_data = {}
        category_values = {}
        if button == "Vše":
            categories = list(Downtime.objects.values_list('category_by_production', flat=True).distinct('category_by_production'))
            for category in categories:
                category_values[category] = []
            for category in categories:
                for day in days_in_range:
                    datetime_to = datetime.datetime.combine(day, datetime.datetime.min.time())
                    datetime_from = datetime.datetime.combine(day + datetime.timedelta(days=1), datetime.datetime.min.time())
                    category_value = list(Downtime.objects.filter(category_by_production = category, downtime_date = datetime_from).annotate(duration=(F("downtime_end") - F("downtime_start"))).annotate(total_duration=Sum('duration'), total_quantity=Count('duration')).values_list('total_duration', 'total_quantity'))
                    if len(category_value) > 0:    
                        category_values[category].append((day, (category_value[0][0]).total_seconds() / 60, category_value[0][1]))
                    else:
                        category_values[category].append((day, 0, 0))
        else:
            downtimes = list(Downtime.objects.filter(category_by_production=Category.objects.get(category=button), downtime_date__gte=DateFrom, downtime_date__lte=DateTo).values_list('category_by_logistics__category', flat=True).distinct('category_by_logistics__category'))
            for downtime in downtimes:
                category_values[downtime] = []
            for downtime in downtimes:
                for day in days_in_range:
                    datetime_to = datetime.datetime.combine(day, datetime.datetime.min.time())
                    datetime_from = datetime.datetime.combine(day + datetime.timedelta(days=1), datetime.datetime.min.time())
                    category_value = list(Downtime.objects.filter(category_by_production = Category.objects.get(category = button), downtime_date = datetime_from).annotate(duration=(F("downtime_end") - F("downtime_start"))).annotate(total_duration=Sum('duration'), total_quantity=Count('duration')).values_list('total_duration', 'total_quantity'))
                    if len(category_value) > 0:    
                        category_values[downtime].append((day, (category_value[0][0]).total_seconds() / 60, category_value[0][1]))
                    else:
                        category_values[downtime].append((day, 0, 0))
        datasets1 = []
        datasets2 = []
        used_colors = {}
        for category in category_values:
            dataset = {}
            dataset['label'], dataset['data'], dataset['tooltips'] = category, [], []
            for data in category_values[category]:
                dataset['data'].append(data[1])
            color, used_colors = setColor(category, used_colors)
            dataset['borderColor'] = color
            for data in category_values[category]:
                dataset['tooltips'].append(f"Četnost: {data[2]}|Trvání: {data[1]/60}")
            datasets1.append(dataset)
        for category in category_values:
            dataset = {}
            dataset['label'], dataset['data'], dataset['tooltips'] = category, [], []
            for data in category_values[category]:
                dataset['data'].append(data[2])
            color, used_colors = setColor(category, used_colors)
            dataset['borderColor'] = color
            for data in category_values[category]:
                dataset['tooltips'].append(f"Četnost: {data[2]}|Trvání: {data[1]/60}")
            datasets2.append(dataset)

        seconds_in_first_interval_without_sorting = {}
        for category in datasets1:
            category_in_iteration = category['label']
            seconds_in_first_interval_without_sorting[category_in_iteration] = sum(category['data']) / 60 # na minuty
        
        seconds_in_first_interval = dict(sorted(seconds_in_first_interval_without_sorting.items(), key=operator.itemgetter(1), reverse=True))
        barchart_dict = {}
        keys_in_intervals = [*seconds_in_first_interval]
        for key in keys_in_intervals:
            barchart_dict[key] = []
            time = 0
            if key in seconds_in_first_interval:
                time += seconds_in_first_interval[key]
            barchart_dict[key].append(time)
            if key in seconds_in_first_interval:
                barchart_dict[key].append(seconds_in_first_interval[key])
            else:
                barchart_dict[key].append(0)
        
        barchart_dict = dict(sorted(barchart_dict.items(), key=operator.itemgetter(1),reverse=True))

        return_data = {
            'days_first': days,
            'days_in_range_first': days_in_range,
            'datasets1': datasets1,
            'days_second': days,
            'days_in_range_second': days_in_range,
            'datasets2': datasets2,
            'barchart_dict': barchart_dict
        }
        return JsonResponse(return_data)
    if request.method == "GET":
        return render(request, 'visualization.html', {})
    

@login_required
@csrf_exempt
def enter_logistics_downtime(request):
    if request.method == "GET":
        return_data = {}
        production_areas = ProductionArea.objects.all()

        for production_area in production_areas:
            return_data[production_area.name] = {}

            area_lines = Line.objects.filter(production_area=production_area)

            for line in area_lines:
                return_data[production_area.name][line.name] = TrainCircuit.objects.get(line=line).number

        categories = {}

        for category in Category.objects.all().order_by('category'):
            categories[category.category] = list(category.subcategory_set.all().values_list('subcategory', flat=True))

        context = {
            'data': return_data,
            'profile': Profile.objects.get(user=request.user),
            'categories': categories,
            'train_drivers': list(TrainDriver.objects.order_by('train_driver').values_list('train_driver', flat=True)),
            'train_circuits': TrainCircuit.objects.distinct('number').values_list('number', flat=True)
        }
        
        return render(request, 'enter_logistics_downtime.html', context)

    if request.method == "POST":
        if 'image' in request.FILES:
            file = request.FILES['image']
            path = default_storage.save(f'logistics_imgs/{request.POST.get("Id")}_.png', ContentFile(file.read()))
        creates = {}
        creates['id'] = request.POST.get('Id')
        creates['production_area'] = ProductionArea.objects.get(name = request.POST.get('ProductionArea')) 
        creates['downtime_date'] = datetime.datetime.strptime(request.POST.get('Date'), "%Y-%m-%d").date()
        creates['shift'] = request.POST.get('Shift') 
        creates['recorded_by'] = request.POST.get('Noticed')
        creates['train_driver'] = TrainDriver.objects.get_or_create(train_driver=request.POST.get('TrainDriver'))[0]
        creates['category_by_production'] = Category.objects.filter(category = request.POST.get('CategoryByProduction'))
        creates['line'] = Line.objects.filter(name = request.POST.get('Line')).first()
        creates['train_circuit'] = TrainCircuit.objects.filter(number = request.POST.get('TrainCircuit'), line = creates['line']).first()
        creates['order_number'] = request.POST.get('Ordernumber')
        creates['material_number'] = request.POST.get('MaterialNumber')
        creates['downtime_start'] = datetime.datetime.strptime(request.POST.get('TimeFrom'), '%Y-%m-%dT%H:%M')
        creates['downtime_end'] = datetime.datetime.strptime(request.POST.get('TimeTo'), '%Y-%m-%dT%H:%M')
        creates['category_by_production'] = Category.objects.filter(category = request.POST.get('CategoryByProduction')).first()
        creates['subcategory_by_production'] = Subcategory.objects.get_or_create(subcategory = request.POST.get('SubcategoryByProduction'), category = creates['category_by_production'])[0]
        creates['note_by_production'] = request.POST.get('NotesByProduction')
        creates['is_downtime_by_production'] = True if request.POST.get('DowntimeByProduction') == "on" else False

        downtime_object = Downtime.objects.create(**creates)

        sendmail('new', downtime_object)

        return redirect('logistics:show_downtimes')


@login_required
def show_downtimes(request):
    downtimes = Downtime.objects.all().order_by('-downtime_end').annotate(downtime_end_trunc=Trunc('downtime_end', 'second', output_field=DateTimeField())).annotate(downtime_start_trunc=Trunc('downtime_start', 'second', output_field=DateTimeField())).annotate(duration=Sum(F("downtime_end_trunc") - F("downtime_start_trunc")))

    context = {
        'downtimes': downtimes,
    }
    return render(request, 'show_downtimes.html', context)


def fetch_external_downtimes(request):
    fp09_downtimes = DowntimeFromLine.objects.filter(category='Logistic / Logistika', beginning_t__gte='2022-04-01', end_t__lte=str(datetime.datetime.now()))

    for fp09_downtime in fp09_downtimes:
        downtime, created = Downtime.objects.update_or_create(is_external = True, production_area = ProductionArea.objects.get(name='FP'), external_downtime_id=fp09_downtime.id, external_line='FP09', defaults = {'downtime_date': fp09_downtime.beginning_t, 'train_circuit': TrainCircuit.objects.get(line=Line.objects.get(name='FP09')), 'is_downtime_by_production': True, 'downtime_start': fp09_downtime.beginning_t, 'downtime_end': fp09_downtime.end_t, 'note_by_production': fp09_downtime.comment, 'line': Line.objects.get(name='FP09'), 'category_by_production': Category.objects.get(category='Jiné'), 'subcategory_by_production': Subcategory.objects.get_or_create(subcategory = fp09_downtime.downtime if fp09_downtime.downtime else (fp09_downtime.comment if fp09_downtime.comment else ""), category = Category.objects.get(category='Jiné'))[0]})

        if created:
            sendmail('new', downtime)

    fill_in_shifts()

    return HttpResponse('finished')


@login_required
def edit_downtime(request):
    if request.method == "GET":
        return_data = {}
        production_areas = ProductionArea.objects.all()

        for production_area in production_areas:
            return_data[production_area.name] = {}

            area_lines = Line.objects.filter(production_area=production_area)

            for line in area_lines:
                return_data[production_area.name][line.name] = TrainCircuit.objects.get(line=line).number

        categories = {}

        for category in Category.objects.all().order_by('category'):
            categories[category.category] = list(category.subcategory_set.all().values_list('subcategory', flat=True))

        context = {
            'data': return_data,
            'profile': Profile.objects.get(user=request.user),
            'categories': categories,
            'train_drivers': TrainDriver.objects.order_by('train_driver'),
            'train_drivers_list': list(TrainDriver.objects.values_list('train_driver', flat=True)),
            'downtime': Downtime.objects.get(id=request.GET['downtime_id']),
        }
    
        return render(request, 'edit_downtime.html', context)

    if request.method == "POST":
        updates = {}
        if 'image' in request.FILES:
            file = request.FILES['image']
            path = default_storage.save(f'logistics_imgs/{request.POST.get("Id")}_.png', ContentFile(file.read()))
        updates['id'] = request.POST.get('Id')
        updates['production_area'] = ProductionArea.objects.get(name = request.POST.get('ProductionArea')) 
        updates['downtime_date'] = datetime.datetime.strptime(request.POST.get('Date'), "%Y-%m-%d").date()
        updates['shift'] = request.POST.get('Shift') 
        updates['recorded_by'] = request.POST.get('Noticed')
        updates['train_driver'] = TrainDriver.objects.get_or_create(train_driver = request.POST.get('TrainDriver'))[0]
        updates['line'] = Line.objects.filter(name = request.POST.get('Line')).first()
        updates['train_circuit'] = TrainCircuit.objects.filter(number = request.POST.get('TrainCircuit'), line = updates['line']).first()
        updates['order_number'] = request.POST.get('Ordernumber')
        updates['material_number'] = request.POST.get('MaterialNumber')
        updates['downtime_start'] = datetime.datetime.strptime(request.POST.get('TimeFrom'), '%Y-%m-%dT%H:%M')
        updates['downtime_end'] = datetime.datetime.strptime(request.POST.get('TimeTo'), '%Y-%m-%dT%H:%M')
        if Profile.objects.get(user=request.user).role == "Logistics":
            updates['category_by_logistics'] = Category.objects.filter(category = request.POST.get('CategoryByLogistics')).first()
            updates['subcategory_by_logistics'] = Subcategory.objects.get_or_create(subcategory = request.POST.get('SubcategoryByLogistics'), category = updates['category_by_logistics'])[0]
            updates['note_by_logistics'] = request.POST.get('NotesByLogistics') if request.POST.get('NotesByLogistics') != None else ''
            updates['is_downtime_by_logistics'] = True if request.POST.get('DowntimeByLogistics') == 'on' else False
            updates['downtime_rootcause'] = request.POST.get('Rootcause')
            updates['deadline'] = datetime.datetime.strptime(request.POST.get('Deadline'), '%Y-%m-%d')
            updates['corrective_action'] = request.POST.get('CorrectiveAction')
            updates['responsible'] = request.POST.get('Responsible')
            updates['decoded_by'] = request.POST.get('DecodedBy')
            updates['status'] = request.POST.get('Status')
            updates['logistics_deduction'] = request.POST.get('Deduction')
        else:
            updates['category_by_production'] = Category.objects.filter(category = request.POST.get('CategoryByProduction')).first()
            updates['subcategory_by_production'] = Subcategory.objects.get_or_create(subcategory = request.POST.get('SubcategoryByProduction'), category = updates['category_by_production'])[0]
            updates['note_by_production'] = request.POST.get('Notes') if request.POST.get('Notes') != None else ''
            updates['is_downtime_by_production'] = True if request.POST.get('DowntimeByProduction') == 'on' else False

        Downtime.objects.filter(id=updates['id']).update(**updates)

        sendmail('edit', Downtime.objects.get(id=updates['id']))

        return redirect('logistics:show_downtimes')

def setColor(category, used_colors):
    if category == 'Obaly':
        color = 'rgb(4, 57, 89)'
    elif category == 'Plánování':
        color = 'rgb(10, 75, 120)'
    elif category == 'Systém':
        color = 'rgb(94, 150, 19)'
    elif category == 'Zaměstnanci':
        color = 'rgb(34, 113, 177)'
    elif category == 'Technika':
        color = 'rgb(53, 130, 196)'
    elif category == 'Výroba':
        color = 'rgb(120, 124, 130)'
    elif category == 'Kvalita':
        color = 'rgb(100, 105, 112)'
    elif category == 'Procesy':
        color = 'rgb(80, 87, 94)'
    elif category == 'Komunikace':
        color = 'rgb(60, 67, 74)'
    elif category == 'Jiné':
        color = 'rgb(44, 51, 56)'
    else:
        if category in used_colors:
            color = used_colors[category]
        else:
            r = random.randint(0,255)
            g = random.randint(0,255)
            b = random.randint(0,255)
            color = f'rgb({r}, {g}, {b})'
            used_colors[category] = color
    return color, used_colors


@csrf_exempt
def definitions(request):     
    if request.method == "GET":
        context = {
            'data': [
                {
                    'label': 'kategorie',
                    'tag': 'category',
                    'alias': 'category',
                    'objects': Category.objects.all(),
                    'child': ['podkategorie', 'subcategory'],
                    'deletable': True,
                    'editable': False,
                    'addable': True,
                },
                {
                    'label': 'subkategorie',
                    'tag': 'subcategory',
                    'alias': 'subcategory',
                    'objects': Subcategory.objects.all(),
                    'parent': ['kategorie', 'category'],
                    'editable': False,
                    'deletable': True,
                    'addable': True,
                },
                {
                    'label': 'řidiči',
                    'tag': 'train_driver',
                    'alias': 'train_driver',
                    'objects': TrainDriver.objects.all(),
                    'editable': False,
                    'deletable': True,
                    'addable': True,
                },
                {
                    'label': 'výrobní oblast',
                    'tag': 'production_area',
                    'alias': 'name',
                    'objects': ProductionArea.objects.all(),
                    'child': ['linky', 'line'],
                    'editable': False,
                    'deletable': True,
                    'addable': True,
                },
                {
                    'label': 'linky',
                    'tag': 'line',
                    'alias': 'name',
                    'objects': Line.objects.all(),
                    'parent': ['výrobní oblast', 'production_area'],
                    'child': ['vlakové okruhy', 'train_circuit'],
                    'editable': False,
                    'deletable': True,
                    'addable': True,
                },
                {
                    'label': 'vlakové okruhy',
                    'tag': 'train_circuit',
                    'alias': 'number',
                    'objects': TrainCircuit.objects.all().distinct('number'),
                    'parent': ['linky', 'line'],
                    'editable': True,
                    'deletable': False,
                    'addable': False,
                },
                {
                    'label': 'role',
                    'tag': 'profile',
                    'alias': 'user',
                    'objects': Profile.objects.all().order_by('user__last_name'),
                    'editable': True,
                    'deletable': True,
                    'addable': True,
                }
            ]
        }

        return render(request, 'definitions.html', context)

    if request.method == "POST":
        request_data = json.loads(request.body)

        def add(data):
            if data['class'] == 'category':
                Category.objects.create(category = data['item'])
            if data['class'] == 'subcategory':
                Subcategory.objects.create(subcategory = data['item'], category = Category.objects.get(category = data['parentValue']))        
            if data['class'] == 'train_driver':
                TrainDriver.objects.create(train_driver = data['item'])
            if data['class'] == 'line':
                line_object = Line.objects.create(name = data['item'], production_area = ProductionArea.objects.get(name = data['parentValue']))
                TrainCircuit.objects.create(line = line_object, number = 0)
            if data['class'] == 'production_area':
                ProductionArea.objects.create(name = data['item'])
            if data['class'] == 'profile':
                last_name = data['item'].split(", ")[0]
                first_name = data['item'].split(", ")[1]
                username = f'{last_name[:7]}{first_name[0]}'
                email = f'{first_name}.{last_name}@knorr-bremse.com'
                if User.objects.filter(last_name=last_name, first_name=first_name).exists():
                    user = User.objects.get(last_name=last_name, first_name=first_name)
                else:
                    user = User.objects.create_user(remove_accents(username), remove_accents(email), 'Liberec24680', first_name=first_name.capitalize(), last_name=last_name.capitalize())
                profile, created = Profile.objects.get_or_create(user = user, defaults={'role': 'Logistics'})
            return JsonResponse({'status': 'okay'})
            
        def get(data):
            if data['child_class'] == 'subcategory':
                return JsonResponse({'items' : list(Subcategory.objects.filter(category = Category.objects.get(category=data['selected_value'])).order_by('id').values_list('subcategory', flat=True))})
            if data['child_class'] == 'line':
                return JsonResponse({'items' : list(Line.objects.filter(production_area = ProductionArea.objects.get(name=data['selected_value'])).values_list('name', flat=True))})
            if data['child_class'] == 'train_circuit':
                return JsonResponse({'items' : list(TrainCircuit.objects.filter(line = Line.objects.get(name=data['selected_value'])).values_list('number', flat=True))})

        def delete(data):
            if data['class'] == 'production_area':
                ProductionArea.objects.filter(name = data['item']).delete()
            if data['class'] == 'category':
                Category.objects.filter(category = data['item']).delete()
            if data['class'] == 'subcategory':
                Subcategory.objects.filter(subcategory = data['item']).delete()
            if data['class'] == 'train_driver':
                TrainDriver.objects.filter(train_driver = data['item']).delete()
            if data['class'] == 'line':
                Line.objects.filter(name = data['item']).delete()
            if data['class'] == 'profile':
                Profile.objects.filter(user = User.objects.get(last_name=data['item'].split(", ")[0], first_name=data['item'].split(", ")[1])).delete()
            return JsonResponse({'status': 'okay'})

        if request_data['action'] == 'add':
            return add(request_data)
        elif request_data['action'] == 'get':
            return get(request_data)
        elif request_data['action'] == 'delete':
            return delete(request_data)


def remove_accents(accented_string):
    new = accented_string.lower()
    new = re.sub(r'[àáâãäå]', 'a', new)
    new = re.sub(r'[èéêë]', 'e', new)
    new = re.sub(r'[ìíîï]', 'i', new)
    new = re.sub(r'[òóôõö]', 'o', new)
    new = re.sub(r'[ùúûü]', 'u', new)
    new = re.sub(r'[č]', 'c', new)
    new = re.sub(r'[š]', 's', new)
    new = re.sub(r'[ž]', 'z', new)
    new = re.sub(r'[ř]', 'r', new)
    new = re.sub(r'[ť]', 't', new)
    new = re.sub(r'[ň]', 'n', new)
    new = re.sub(r'[ď]', 'd', new)
    new = re.sub(r'[ě]', 'e', new)
    new = re.sub(r'[ý]', 'y', new)
    return new


def send_email_daily_frontend(request):
    now = datetime.datetime.now()
    weekday_today = datetime.datetime.today().weekday()
    if weekday_today > 0 and weekday_today < 5:
        now_timedelta24h = now - datetime.timedelta(hours=24)
        downtimes = Downtime.objects.filter(downtime_start__gte = now_timedelta24h).order_by('-downtime_end').annotate(downtime_end_trunc=Trunc('downtime_end', 'second', output_field=DateTimeField())).annotate(downtime_start_trunc=Trunc('downtime_start', 'second', output_field=DateTimeField())).annotate(duration=Sum(F("downtime_end_trunc") - F("downtime_start_trunc")))
    elif weekday_today == 0:
        now_timedelta72h = now - datetime.timedelta(hours=72)
        downtimes = Downtime.objects.filter(downtime_start__gte = now_timedelta72h).order_by('-downtime_end').annotate(downtime_end_trunc=Trunc('downtime_end', 'second', output_field=DateTimeField())).annotate(downtime_start_trunc=Trunc('downtime_start', 'second', output_field=DateTimeField())).annotate(duration=Sum(F("downtime_end_trunc") - F("downtime_start_trunc")))
    else:
        downtimes = []
    context = {
        'downtimes': downtimes,
    }
    if weekday_today < 5:
        send_email_daily(downtimes)
        return render(request, 'send_email_daily.html', context)
    else:
        return HttpResponse('Not working day')

def send_email_daily(downtimes):
    html_template = 'send_email_daily.html'
    from_email = 'automat@knorr-bremse.com'
    html_message = render_to_string(html_template, { 'downtimes': downtimes })
    subject = 'Logistické prostoje za posledních 24 hodin'
    #send_to = ['Patrik.Zach@knorr-bremse.com']
    send_to = ['DLLIBlogisticsdowntimes@knorr-bremse.com', 'DLLIBshiftleader@knorr-bremse.com']
    message = EmailMessage(subject, html_message, from_email, send_to)
    message.content_subtype = 'html'
    message.send()

def sendmail(type, downtime_object, from_email='automat@knorr-bremse.com'):

    if type == 'new':
        subject = f'Nový logistický prostoj, identifikace: {downtime_object.id}'
        emails = EmailNotification.objects.all()
        send_to = []

        for email in emails:
            if email.notify_on_create:
                if (email.notify_local_only and downtime_object.production_area in ProductionArea.objects.filter(responsible = email.profile)) or email.notify_global:
                    send_to.append(email.email)
    else:
        subject = f'Logistický prostoj byl upraven, identifikace: {downtime_object.id}'
        emails = EmailNotification.objects.all()
        send_to = []

        for email in emails:
            if email.notify_on_update:
                if (email.notify_local_only and downtime_object.production_area in ProductionArea.objects.filter(responsible = email.profile)) or email.notify_global:
                    send_to.append(email.email)

    html_template = 'email_message.html'

    html_message = render_to_string(html_template, { 'downtime': downtime_object })

    message = EmailMessage(subject, html_message, from_email, send_to)
    message.content_subtype = 'html'
    message.send()
    

@login_required
def profile(request, user_full_name):
    user = User.objects.get(last_name = user_full_name.split(", ")[0], first_name = user_full_name.split(", ")[1])
    profile, created = Profile.objects.get_or_create(user = user, defaults={'role': 'Production'})
    email, created = EmailNotification.objects.get_or_create(profile=profile)

    context = {
        'production_areas': ProductionArea.objects.all().order_by('name'),
        'profile': profile,
        'email': email,
    }

    if request.method == "POST":
        if 'email' in request.POST:
            email_address = request.POST.get('email')
            email.email = email_address
        if 'role' in request.POST:
            role = request.POST.get('role')
            profile.role = role
        if 'production-area' in request.POST:
            profile_responsible_areas = ProductionArea.objects.filter(responsible=profile)
            for production_area in profile_responsible_areas: # remove all production areas responsibilities first...
                production_area.responsible.remove(profile)
            for requested_production_area_id in request.POST.getlist('production-area'):
                production_area = ProductionArea.objects.get(id = requested_production_area_id)
                production_area.responsible.add(profile)
                production_area.save()
        if 'notification-on-create' in request.POST:
            email.notify_on_create = True
        else:
            email.notify_on_create = False
        if 'notification-on-update' in request.POST:
            email.notify_on_update = True
        else:
            email.notify_on_update = False
        if 'global' in request.POST:
            email.notify_global = True if request.POST.get('global') == 'global' else False
            email.notify_local_only = True if request.POST.get('global') == 'local-only' else False

        email.save()
        profile.save()

    return render(request, 'profile.html', context)


def train_circuit(request, train_circuit_number, line_name):
    line = Line.objects.get(name = line_name)
    train_circuits = TrainCircuit.objects.distinct('number')

    context = {
        'train_circuit_number': train_circuit_number,
        'train_circuits': train_circuits,
        'line': line,
    }

    if request.method == "POST":
        original_train_circuit = TrainCircuit.objects.get(number = train_circuit_number, line = line)
        original_train_circuit.number = request.POST.get('train_circuit')
        original_train_circuit.save()

        return redirect('logistics:definitions')


    return render(request, 'train_circuit.html', context)


@csrf_exempt
def get_downtime_details(request):
    date = datetime.datetime.strptime(request.POST.get('date'), "%Y-%m-%d")
    try:
        line = Line.objects.get(name = request.POST.get('line'))

        return_value = Downtime.objects.filter(downtime_date__gte=date, downtime_date__lt=date + datetime.timedelta(days=1), is_downtime_by_production=True, line = line).annotate(duration=F("downtime_end") - F("downtime_start")).aggregate(duration_d=Sum('duration'))['duration_d']

        # return HttpResponse( round(return_value.total_seconds() / 60 - Downtime.objects.filter(downtime_date__gte=date, downtime_date__lt=date + datetime.timedelta(days=1), is_downtime_by_production=True, line = line).aggregate(deduction=Sum('logistics_deduction'))['deduction']), 0 )
        return HttpResponse( int(round(return_value.total_seconds() / 60, 0)))
    except:
        return HttpResponse("0")


@csrf_exempt
def get_category(request):
    date = datetime.datetime.strptime(request.POST.get('date'), "%Y-%m-%d")
    try:
        line = Line.objects.get(name = request.POST.get('line'))

        return_value = Downtime.objects.filter(downtime_date__gte=date, downtime_date__lt=date + datetime.timedelta(days=1), is_downtime_by_production=True, line = line).values_list('category_by_production', flat=True)

        return HttpResponse(return_value)
    except:
        return HttpResponse("")


def fill_in_shifts():
    downtimes_without_team = Downtime.objects.filter(shift__exact='', line = Line.objects.get(name='FP09'))
    for downtime in downtimes_without_team:
        downtime.shift = Shift.objects.filter(shift_beginning__lte=downtime.downtime_start).order_by('-shift_beginning').first().team
        downtime.save()


@csrf_exempt
def get_sum_for_report(request):
    shift = request.POST.get('shift')
    month = int(request.POST.get('month'))
    year = int(request.POST.get('year'))
    beginning = datetime.datetime(year, month, 1)
    next_month = (beginning + datetime.timedelta(days = 32)).replace(day = 1)
    lines = Line.objects.filter(production_area=ProductionArea.objects.get(name=request.POST.get('line'))) if ProductionArea.objects.filter(name = request.POST.get('line')).exists() else Line.objects.all()

    return_value = Downtime.objects.filter(downtime_date__gte=beginning, downtime_date__lt=next_month, is_downtime_by_logistics=True, shift=shift, line__in=lines).annotate(duration=F("downtime_end") - F("downtime_start")).aggregate(duration_d=Sum('duration'))['duration_d']
    
    try:
        return HttpResponse(str(return_value.total_seconds()/60))
    except:
        return HttpResponse(str(0))

