from django.shortcuts import render
from django.http import HttpResponse
from .models import QM02
from email.message import EmailMessage
from threading import Thread
import smtplib


def excel_to_db(request):

    print(request.GET)

    params = {}
    params['area'] = request.GET.get('area')
    params['q2_report_number'] = request.GET.get('q2_report_number')
    params['excel_row'] = request.GET.get('excel_row')
    params['total_costs'] =  float(request.GET.get('total_costs').replace(",", "."))
    params['other_costs'] = float(request.GET.get('other_costs').replace(",", "."))
    params['responsible_department'] = request.GET.get('responsible_department')
    params['responsible_person'] = request.GET.get('responsible_person')
    params['reason_comment'] = request.GET.get('reason_comment')
    params['line_loss'] = float(request.GET.get('line_loss').replace(",", "."))
    params['reason_long_text'] = request.GET.get('reason_long_text')
    params['reduction'] = float(request.GET.get('reduction').replace(",", "."))
    params['to_be_invoiced'] = float(request.GET.get('to_be_invoiced').replace(",", "."))
    params['extra_costs_code'] = request.GET.get('extra_costs_code')
    params['resource'] = request.GET.get('resource')
    params['quantity'] = float(request.GET.get('quantity').replace(",", "."))
    params['qm_code'] = request.GET.get('qm_code')
    params['unit'] = request.GET.get('unit')



    qm_obj = QM02.objects.update_or_create(
        excel_row=request.GET.get('excel_row'), 
        area=request.GET.get('area'), 
        defaults=params,
        )

    Thread(target=sendmail, args=(None, "<h1>Ano!</h1>", f"{params['q2_report_number']} byla schválena manažerem!", request.GET.get('mail_address'))).start()

    return HttpResponse("OK")


def sendmail(request=None, message_content=None, subject=None, recipient=None, cc='peter.vajda@knorr-bremse.com'):

    if request:
        message_content = request.GET.get('message_content')
        subject = request.GET.get('subject')
        recipient = request.GET.get('recipient')

    msg = EmailMessage()

    msg['Subject'] = subject
    msg['From'] = "automat@knorr-bremse.com"
    msg['To'] = recipient
    msg['Cc'] = cc
    msg.set_content(message_content, subtype='html')

    s = smtplib.SMTP('smtp-relay.corp.knorr-bremse.com')
    s.send_message(msg)
    s.quit()