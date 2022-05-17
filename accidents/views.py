from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponse
from burza.models import Worker
from django.contrib.auth.models import User
import smtplib
from .models import HashedPicture, Accident, InjuryType, Bodypart, Nearmiss, CorrectiveAction
import json
import os
from unidecode import unidecode
from django.core.files.storage import FileSystemStorage
import random
import string
from django.conf import settings
from Knorr.settings import TEMPORARY_IMAGES_ROOT, MEDIA_ROOT
import datetime
from django.core.files import File
from email.message import EmailMessage
from django.contrib.auth.decorators import login_required
from django.core import serializers



def accidents_home(request):
    context = {}

    return render(request, 'accidents_home.html', context)


@login_required
def form_nearmiss(request, nearmiss_id=False):
    context = {}

    if nearmiss_id and request.method == "POST":
        context.update({
            'message': True,
        })

    workers = list(Worker.objects.values_list('name', flat=True))
    workers_reversed_names = [str(name_string.split(' ', 1)[1] + ' ' + name_string.split(' ', 1)[0])for name_string in workers]
    workers_list = ', '.join(workers_reversed_names)

    context.update({
        'workers': workers_list,
    })

    if nearmiss_id:
        context.update({
            'form': Nearmiss.objects.get(id=nearmiss_id)
        })

    if request.method == "POST":

        updates = {}
        urls = {}

        dict_request = dict(request.POST)

        for key, value in dict_request.items():
            if value[0]:
                if key in ['reporter_role', 'place', 'activity_nearmiss', 'nearmiss_launcher', 'nearmiss_rootcause', 'nearmiss_description', 'immediate_corrective_measures',  'protocol_datetime', 'protocol_author_role']:
                    try:
                        updates[key] = value[0]
                    except:
                        pass

                if key == 'personal_number':
                    workerObject = Worker.objects.get(personal_number=int(value[0]))
                    updates['reporter'] = workerObject
                    manager = workerObject.manager
                    managerObject = User.objects.get(last_name=manager.split(" ")[0], first_name=manager.split(" ")[1])

                if key == 'nearmiss_date':
                    nearmissDate = datetime.datetime.strptime(value[0], '%Y-%m-%d')

                if key == 'nearmiss_time':
                    nearmissTime = datetime.datetime.strptime(value[0], '%H:%M').time()
                    nearmissDateTime = datetime.datetime.combine(nearmissDate, nearmissTime)
                    updates['datetime_of_nearmiss'] = nearmissDateTime

                if key == 'filepond':
                    for hashed_name in value:
                        fs_source = FileSystemStorage(location=TEMPORARY_IMAGES_ROOT)
                        fs_target = FileSystemStorage(location=MEDIA_ROOT)
                        initial_path = fs_source.path(hashed_name)
                        re_name = HashedPicture.objects.values_list('filename', flat=True).get(hashed_name=hashed_name)
                        new_path = settings.MEDIA_ROOT + '/' + re_name
                        os.rename(initial_path, new_path)
                        urls[re_name] = fs_target.url(re_name)

                if key == 'fmea_implementation':
                    fmea_implementation = datetime.datetime.strptime(value[0], '%Y-%m-%d')
                    updates['fmea_implementation'] = fmea_implementation

                if key == 'sos_revision':
                    sos_revision = datetime.datetime.strptime(value[0], '%Y-%m-%d')
                    updates['sos_revision'] = sos_revision
                    updates['fmea_relevant'] = True
            else:
                if key == 'sos_revision':
                    updates['fmea_relevant'] = False
                    updates['sos_revision'] = None
                if key == 'fmea_implementation':
                    updates['fmea_implementation'] = None
                    updates['fmea_relevant'] = False

        if not nearmiss_id:
            nearmissObject = Nearmiss.objects.create(**updates)
            nearmiss_urls = nearmissObject.image_urls
            correctiveActionObject = CorrectiveAction.objects.create(nearmiss=nearmissObject)

            if urls:
                for fname, furl in urls.items():
                    nearmiss_urls[fname] = furl
            nearmissObject.image_urls = nearmiss_urls
            nearmissObject.save()

            message_content = 'Nová skoronehoda!<br /><a href="' + request.build_absolute_uri(reverse('form_nearmiss', kwargs={'nearmiss_id' : nearmissObject.id})) + '">Zápis zde</a>'
            subject = "Nová skoronehoda"
            # recipients = ["peter.vajda@knorr-bremse.com", managerObject.email]
            recipients = ["ondrej.kracalik@knorr-bremse.com", "jan.husak@knorr-bremse.com"]

            sendmail(message_content, subject, recipients, cc='peter.vajda@knorr-bremse.com')

        else:
            Nearmiss.objects.filter(id=nearmiss_id).update(**updates)
            nearmissObject = Nearmiss.objects.get(id=accident_id)
            nearmiss_urls = nearmissObject.image_urls
            for fname, furl in urls.items():
                nearmiss_urls[fname] = furl
            nearmissObject.image_urls = nearmiss_urls
            nearmissObject.save()


        return redirect(form_nearmiss, nearmissObject.id)
    
    return render(request, 'form_nearmiss.html', context)



def accidents_overview(request):

    correctiveActionObjects = CorrectiveAction.objects.all().order_by('accident_id', 'id')
    
    workers = list(Worker.objects.values_list('name', flat=True))
    workers_reversed_names = [str(name_string.split(' ', 1)[1] + ' ' + name_string.split(' ', 1)[0])for name_string in workers]
    workers_list = ', '.join(workers_reversed_names)
    
    context = {
        'corrective_actions': correctiveActionObjects,
        'workers': workers_list,
    }

    return render(request, 'accidents_overview.html', context)
    
@login_required    
def form_injury(request, accident_id=False):
    context = {}

    if accident_id and request.method == "POST":
        context.update({
            'message': True,
        })

    workers = list(Worker.objects.values_list('name', flat=True))
    workers_reversed_names = [str(name_string.split(' ', 1)[1] + ' ' + name_string.split(' ', 1)[0])for name_string in workers]
    workers_list = ', '.join(workers_reversed_names)

    context.update({
        'workers': workers_list,
        'injury_types': InjuryType.objects.all().order_by('injury_type'),
        'bodyparts': Bodypart.objects.all().order_by('bodypart'),
    })

    if accident_id:
        context.update({
            'form': Accident.objects.get(id=accident_id)
        })

    if request.method == "POST":

        print(request.POST)

        updates = {}
        urls = {}

        dict_request = dict(request.POST)

        for key, value in dict_request.items():
            if value[0]:
                if key in ['dob', 'injured_role', 'bozp_aware', 'on_workplace_since', 'count_of_injured', 'injured_bodypart', 'accident_injury_type', 'hours_worked_before_accident', 'injury_type', 'place', 'activity_injury', 'injury_launcher', 'injury_rootcause', 'workplace_wrong', 'employee_wrong', 'accident_influenced_by',  'accident_description', 'immediate_corrective_measures', 'alcohol_test', 'protocol_datetime', 'protocol_author_role', 'witnesses']:
                    try:
                        updates[key] = value[0]
                    except:
                        pass

                if key == 'personal_number':
                    workerObject = Worker.objects.get(personal_number=int(value[0]))
                    updates['injured'] = workerObject
                    manager = workerObject.manager
                    managerObject = User.objects.get(last_name=manager.split(" ")[0], first_name=manager.split(" ")[1])

                if key == 'accident_date':
                    accidentDate = datetime.datetime.strptime(value[0], '%Y-%m-%d')

                if key == 'accident_time':
                    accidentTime = datetime.datetime.strptime(value[0], '%H:%M').time()
                    accidentDateTime = datetime.datetime.combine(accidentDate, accidentTime)
                    updates['accident_datetime'] = accidentDateTime

                if key == 'filepond':
                    for hashed_name in value:
                        fs_source = FileSystemStorage(location=TEMPORARY_IMAGES_ROOT)
                        fs_target = FileSystemStorage(location=MEDIA_ROOT)
                        initial_path = fs_source.path(hashed_name)
                        re_name = HashedPicture.objects.values_list('filename', flat=True).get(hashed_name=hashed_name)
                        new_path = settings.MEDIA_ROOT + '/' + re_name
                        os.rename(initial_path, new_path)
                        urls[re_name] = fs_target.url(re_name)

                if key == 'fmea_implementation':
                    fmea_implementation = datetime.datetime.strptime(value[0], '%Y-%m-%d')
                    updates['fmea_implementation'] = fmea_implementation

                if key == 'sos_revision':
                    sos_revision = datetime.datetime.strptime(value[0], '%Y-%m-%d')
                    updates['sos_revision'] = sos_revision
                    updates['fmea_relevant'] = True
            else:
                if key == 'sos_revision':
                    updates['fmea_relevant'] = False
                    updates['sos_revision'] = None
                if key == 'fmea_implementation':
                    updates['fmea_implementation'] = None
                    updates['fmea_relevant'] = False


        if not accident_id:
            accidentObject = Accident.objects.create(**updates)
            accident_urls = accidentObject.image_urls
            correctiveActionObject = CorrectiveAction.objects.create(accident=accidentObject)
            accidentObject.save()
            
            
            if urls:
                for fname, furl in urls.items():
                    accident_urls[fname] = furl
            accidentObject.image_urls = accident_urls
            accidentObject.save()
            message_content =  'Nová nehoda!<br /><a href="' + request.build_absolute_uri(reverse('form_injury', kwargs={'accident_id' : accidentObject.id})) + '">Zápis zde</a>'
            subject = "Nová nehoda!"
            # recipients = ["peter.vajda@knorr-bremse.com", managerObject.email]
            recipients = ["ondrej.kracalik@knorr-bremse.com", "jan.husak@knorr-bremse.com"]


            sendmail(message_content, subject, recipients, cc='peter.vajda@knorr-bremse.com')

        else:
            Accident.objects.filter(id=accident_id).update(**updates)
            accidentObject = Accident.objects.get(id=accident_id)
            accident_urls = accidentObject.image_urls
            for fname, furl in urls.items():
                accident_urls[fname] = furl
            accidentObject.image_urls = accident_urls
            accidentObject.save()


        return redirect(form_injury, accidentObject.id)
    
    return render(request, 'form_injury.html', context)


def get_worker_details(request):
    response = request.POST.get('data')

    deserialized_response = json.loads(response)

    name = str(deserialized_response['name'].split(' ', 1)[1] + ' ' + deserialized_response['name'].split(' ', 1)[0])

    workerObject = Worker.objects.get(name=name)

    return_response = dict()

    return_response['personal_number'] = workerObject.personal_number

    return JsonResponse(return_response)
    

def show_accidents(request):
    pass


def process(request):

    for f in request.FILES.getlist('filepond'):
        randstring = get_random_string(15)
        fs = FileSystemStorage(location=TEMPORARY_IMAGES_ROOT)
        filename = fs.save(randstring, f)
        HashedPicture.objects.create(filename=unidecode(f.name).replace(".", "_" + str(random.randint(100,999)) + "."), hashed_name=randstring)

    return HttpResponse(randstring, content_type="text/plain")


def revert(request):

    filename = str(request.body.decode('utf-8'))

    fs = FileSystemStorage(location=TEMPORARY_IMAGES_ROOT)
    fs.delete(filename)

    return HttpResponse("Deleted", content_type="text/plain")


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return(result_str)


def delete_picture(request):
    print(request.POST)

    formObject = Accident.objects.get(id=request.POST.get('data').split(',')[1])
    key_to_remove = request.POST.get('data').split(',')[0]
    formObject.image_urls.pop(key_to_remove)
    formObject.save()

    return None


def sendmail(message_content, subject, recipients, cc='peter.vajda@knorr-bremse.com'):

    from email.message import EmailMessage

    msg = EmailMessage()

    msg['Subject'] = subject
    msg['From'] = "automat@knorr-bremse.com"
    msg['To'] = recipients
    msg['Cc'] = cc
    msg.set_content(message_content, subtype='html')

    s = smtplib.SMTP('smtp-relay.corp.knorr-bremse.com')
    s.send_message(msg)
    s.quit()


def store_data_to_db(request):

    corrective_action_id = request.POST.get('data').split("///")[0]
    attribute = request.POST.get('data').split("///")[1]
    value = request.POST.get('data').split("///")[2]

    correctiveActionObject = CorrectiveAction.objects.get(id=corrective_action_id)
    
    if attribute == 'longterm_corrective_measure':
        correctiveActionObject.longterm_corrective_measure = value
        correctiveActionObject.save()

    if attribute == 'measure_implementation_date':
        correctiveActionObject.measure_implementation_date = datetime.datetime.strptime(value, "%Y-%m-%d")
        correctiveActionObject.save()

    if attribute == 'responsible':
        correctiveActionObject.responsible = value
        correctiveActionObject.save()

    if attribute == 'status':
        correctiveActionObject.status = value
        correctiveActionObject.save()

    if attribute == 'measure_effectiveness':
        correctiveActionObject.measure_effectiveness = value
        correctiveActionObject.save()

    return HttpResponse("Ano")


def add_corrective_measure_for_accident(request, accident_id):

    context = {}

    if request.method == "POST":
        
        accidentObject = Accident.objects.get(id=accident_id)

        correctiveActionObject = CorrectiveAction.objects.create(longterm_corrective_measure=request.POST.get('longterm_corrective_measure'), responsible=request.POST.get('responsible'),  status=request.POST.get('status'), measure_effectiveness=request.POST.get('measure_effectiveness'), measure_implementation_date=request.POST.get('measure_implementation_date'), accident=accidentObject)

    return render(request, 'add_corrective_measure_for_accident.html', context)


def add_corrective_measure_for_nearmiss(request, nearmiss_id):

    context = {}

    if request.method == "POST":
        
        nearmissObject = Nearmiss.objects.get(id=nearmiss_id)

        correctiveActionObject = CorrectiveAction.objects.create(longterm_corrective_measure=request.POST.get('longterm_corrective_measure'), responsible=request.POST.get('responsible'),  status=request.POST.get('status'), measure_effectiveness=request.POST.get('measure_effectiveness'), measure_implementation_date=request.POST.get('measure_implementation_date'), nearmiss=nearmissObject)

    return render(request, 'add_corrective_measure_for_nearmiss.html', context)