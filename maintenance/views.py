from builtins import enumerate, len, print, reversed
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import Line, Part, SpareParts, Columns, UserVisible
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

 

def index(request):

    lines = Line.objects.all()

    return render(request, 'maintenance_index.html', {'lines': lines})


def upload_parts(request): # tohle je pro obecni obrazovku upload parts (master)

    crucial_columns = Columns.objects.filter(crucial=True)
    part_related_columns = Columns.objects.filter(part_related=True).exclude(crucial=True).order_by('label_cz')
    columns_options = list(Columns.objects.filter(part_related=True).order_by('label_cz').values_list('label_cz', flat=True))
    columns_options.append('')

    context = {
        'crucial_columns': crucial_columns,
        'part_related_columns': part_related_columns,
        'columns_options': columns_options,
    }

    return render(request, 'upload_parts.html', context)
    

@csrf_exempt
@login_required
def show_parts(request):
    if request.method == "POST":
        column_technical_name = json.loads(request.body)['columnTechnicalName']
        column = Columns.objects.get(technical_name=column_technical_name)
        checked = json.loads(request.body)['checked']
    
        if checked == "False":
            checked = False

        UserVisible.objects.update_or_create(column=column, user=request.user, defaults={'visible': checked})

    parts = Part.objects.all().order_by('label_2')
    lines = Line.objects.values_list('name', flat=True)
    columns = Columns.objects.filter(part_related=True).order_by('id')
        
    if not UserVisible.objects.filter(user=request.user).exists():
        for column in Columns.objects.filter(visible_by_default=True):
            UserVisible.objects.create(column=column, user=request.user, visible=True)

    context = {
        'parts': parts,
        'lines': lines,
        'columns': columns,
        'user_columns': Columns.objects.filter(id__in=UserVisible.objects.filter(user=request.user, visible=True).values_list('column', flat=True))
    }


    return render(request, 'show_parts.html', context)


def show_parts2(request):
    parts = Part.objects.all()

    context = {
        'parts': parts,
    }


    return render(request, 'show_parts2.html', context)


@csrf_exempt
def save_parts(request): # pro upravu parts (master)

    data = json.loads(request.body)['data']

    for part_id, values in data.items():
        partObject = Part.objects.get(id=part_id)
        for attr, value in values.items():
            if value in ("true", "True"):
                value = True
            if value in ('"false"', "false", "False"):
                value = False
            setattr(partObject, attr, value)
            partObject.save()

    return JsonResponse({'status': 'okay'})


def upload_spare_parts_list(request): # obecna obrazovka pro nahrani seznamu nahradnych dilu pro linku

    lines = Line.objects.values_list('name', flat=True)
    crucial_columns = Columns.objects.filter(crucial=True)
    other_columns = Columns.objects.exclude(crucial=True).order_by('label_cz')
    columns_options = list(Columns.objects.order_by('label_cz').values_list('label_cz', flat=True))
    columns_options.append('')

    context = {
        'crucial_columns': crucial_columns,
        'other_columns': other_columns,
        'columns_options': columns_options,
        'lines': lines,
    }

    return render(request, 'upload_spare_parts_list.html', context)


@csrf_exempt
def check_if_part_exists(request):

    filters = {}

    data = json.loads(request.body)['data']

    columns = Columns.objects.filter(label_cz__in=data.keys())
    technical_names = columns.values_list('technical_name', flat=True)
    local_names = columns.values_list('label_cz', flat=True)

    for index, technical_name in enumerate(technical_names):
        filters[f'{technical_name}__in'] = data[local_names[index]]

    if len(columns) == 1:
        existing_parts = Part.objects.filter(**filters).values_list(*technical_names, flat=True)
        return_data = '|'.join(existing_parts)
    else:
        existing_parts = Part.objects.filter(**filters).values_list(*technical_names)
        return_data = ['|'.join(part) for part in existing_parts]

    return JsonResponse({'data': return_data})


@csrf_exempt
def upload_parts_to_database(request):
    keys = json.loads(request.body)['keys']
    rows = json.loads(request.body)['rows']
    line = json.loads(request.body)['line']

    print(keys)

    delete_indices = []

    for index, item in enumerate(keys):
        if item == '':
            delete_indices.append(index)
    
    print(delete_indices)

    columns = [Columns.objects.get(label_cz=key).technical_name for key in keys if not key in ('', None)]
    print(columns)

    for row in rows:
        for index in reversed(delete_indices):
            del row[index]

    if line:
        line = Line.objects.get(name=line)

    crucial_columns = Columns.objects.filter(crucial=True).values_list('technical_name', flat=True)
    part_related_columns = Columns.objects.filter(part_related=True).exclude(crucial=True).values_list('technical_name', flat=True)
    line_related_columns = Columns.objects.filter(line_related=True).exclude(crucial=True).values_list('technical_name', flat=True)

    for row in rows:
        print(row)
        get_filter = {}
        update_filter_part = {}
        update_filter_line = {}

        for index, column in enumerate(columns):
            if column in crucial_columns:
                get_filter[column] = row[index]
            elif column in part_related_columns:
                update_filter_part[column] = row[index]
            else:
                update_filter_line[column] = row[index]

        part, created = Part.objects.update_or_create(**get_filter, defaults=update_filter_part)

        if line:
            if len(update_filter_line.keys()) > 0:
                spare_part, created = SpareParts.objects.update_or_create(part=part, line=line, defaults=update_filter_line)
            else:
                spare_part, created = SpareParts.objects.update_or_create(part=part, line=line)

    return JsonResponse({'status': 'okay'})


def add_line(request):

    if request.method == "POST":

        line, created = Line.objects.get_or_create(name=request.POST['line'])

        if not created:
            message = "Linka již existuje"
        else:
            message = "Linka úspěšně vytvořena"

        context = {
            'message': message
        }

    else:

        context = {}

    return render(request, 'add_line.html', context)


def remove_line(request):

    return render(request, 'remove_line.html', {})


@csrf_exempt
def remove_parts_from_database(request):
    part_data = json.loads(request.body)
    if part_data['type'] == 'spare-part':
        SpareParts.objects.filter(part=Part.objects.get(id=part_data['id']), line=Line.objects.get(name=part_data['line'])).delete()
        if not SpareParts.objects.filter(part=Part.objects.get(id=part_data['id'])).exists():
            Part.objects.filter(id=part_data['id']).delete()
    if part_data['type'] == 'part':
        SpareParts.objects.filter(part=Part.objects.get(id=part_data['id'])).delete()
        Part.objects.filter(id=part_data['id']).delete()        

    return JsonResponse({'status': 'okay'})


@csrf_exempt
@login_required
def show_parts_from_line(request):

    context = {}

    if request.method == "POST":
        column_technical_name = json.loads(request.body)['columnTechnicalName']
        column = Columns.objects.get(technical_name=column_technical_name)
        checked = json.loads(request.body)['checked']
    
        if checked == "False":
            checked = False

        UserVisible.objects.update_or_create(column=column, user=request.user, defaults={'visible': checked})

    if "line" in request.GET:
        line = Line.objects.get(name = request.GET.get('line'))
        context.update({
            'line': line,
        })
        spare_parts = SpareParts.objects.filter(line=line).order_by('part__label_2')
    else:
        spare_parts = SpareParts.objects.all()

    context.update({
        'spare_parts': spare_parts,
        'columns': Columns.objects.all().order_by('label_cz'),
        'user_columns': Columns.objects.filter(id__in=UserVisible.objects.filter(user=request.user, visible=True).values_list('column', flat=True)),
    })

    return render(request, 'show_parts_from_line.html', context)


@csrf_exempt
def delete_line(request):

    if request.method == "GET":
        return render(request, 'delete_line.html', {'lines': Line.objects.all()})
    else:
        line = Line.objects.get(id=json.loads(request.body)['lineId'])
        spare_parts = SpareParts.objects.filter(line=line)

        for spare_part in spare_parts:
            part_id = spare_part.part.id
            if not SpareParts.objects.filter(part=spare_part.part).exclude(line=line).exists():
                spare_part.delete()
                Part.objects.filter(id=part_id, sap_number__isnull=True).delete()
            else:
                spare_part.delete()

        line.delete()
        return HttpResponse('okay')


@csrf_exempt
def edit_columns(request):

    if request.method == "GET":
        return render(request, 'edit_columns.html', {'columns': Columns.objects.all().order_by('label_cz')})

    if request.method == "POST":
        data = json.loads(request.body)
        column = Columns.objects.get(id=data['id'])
        setattr(column, data['purpose'], data['checked'])
        column.save()

        return JsonResponse({'status': 'ok'})