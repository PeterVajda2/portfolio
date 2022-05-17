from django.urls import path
from .views import index, enter_logistics_downtime, send_email_daily_frontend, visualization, upload_excel, show_downtimes, edit_downtime, definitions, profile, train_circuit, get_downtime_details, fetch_external_downtimes, fill_in_shifts, get_sum_for_report

app_name = "logistics"

urlpatterns = [
    path('logistics', index, name='index'),
    path('logistics/enter_logistics_downtime', enter_logistics_downtime, name='enter_logistics_downtime'),
    path('logistics/visualization', visualization, name='visualization'),
    path('logistics/upload_excel', upload_excel, name='upload_excel'),
    path('logistics/show_downtimes', show_downtimes, name='show_downtimes'),
    path('logistics/edit_downtime', edit_downtime, name='edit_downtime'),
    path('logistics/definitions', definitions, name='definitions'),
    path('logistics/profile/<str:user_full_name>', profile, name='profile'),
    path('logistics/train_circuit/<int:train_circuit_number>/<str:line_name>', train_circuit, name='train_circuit'),
    path('logistics/get_downtime_details', get_downtime_details, name='get_downtime_details'),
    path('logistics/fetch_external_downtimes', fetch_external_downtimes, name='fetch_external_downtimes'),
    path('logistics/fill_in_shifts', fill_in_shifts, name='fill_in_shifts'),
    path('logistics/get_sum_for_report', get_sum_for_report, name='get_sum_for_report'),
    path('logistics/send_email_daily', send_email_daily_frontend, name='send_email_daily')
]