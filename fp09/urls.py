from django.urls import path
from .views import operator_screen, delete_downtime, add_historical_downtimes, pareto_screen_fp09, performance_screen_fp09, get_sum_downtimes, edit_database, alarm_stats, get_fp09_alarm_stats, sync_databases, operator_screen_new, check_for_downtime, fetch_test, fp09_downtime_trends, pair_downtimes, check_for_downtime_auto, downtime_fromline, get_fp09_downtime_fromline, fp09_downtime_trends_2, fp09_downtime_trends_details, split_downtimes, get_stop_line_alarms, downtime_editor, get_fp09_alarms_sum, get_fp09_produced_partnumber, type_details, counter


app_name = "fp09"
urlpatterns = [
    path('fp09/operator', operator_screen, name="operator_screen"),
    path('fp09/operator_new', operator_screen_new, name="operator_screen_new"),
    path('fp09/delete_downtime', delete_downtime, name="delete_downtime"),
    path('fp09/add_historical_downtimes', add_historical_downtimes, name="add_historical_downtimes"),
    path('fp09/pareto_screen', pareto_screen_fp09, name="pareto_screen_fp09"),
    path('fp09/performance_screen', performance_screen_fp09, name="performance_screen_fp09"),
    path('fp09_painting/get_sum_downtimes', get_sum_downtimes, name="get_sum_downtimes"),
    path('fp09/edit_database', edit_database, name="edit_database"),
    path('fp09/alarm_stats', alarm_stats, name="alarm_stats"),
    path('fp09/get_fp09_alarm_stats', get_fp09_alarm_stats, name="get_fp09_alarm_stats"),
    path('fp09/utils/sync_databases', sync_databases, name='sync_databases'),
    path('fp09/utils/check_for_downtime', check_for_downtime, name='check_for_downtime'),
    path('fp09/fetch_test', fetch_test, name='fetch_test'),
    path('fp09/downtime_trends', fp09_downtime_trends, name='fp09_downtime_trends'),
    path('fp09/downtime_trends_2', fp09_downtime_trends_2, name='fp09_downtime_trends_2'),
    path('fp09/downtime_trends_details', fp09_downtime_trends_details, name='fp09_downtime_trends_details'),
    path('fp09/utils/pair_downtimes', pair_downtimes, name='pair_downtimes'),
    path('fp09/utils/downtime_editor', downtime_editor, name='downtime_editor'),
    path('fp09/utils/check_for_downtime_auto', check_for_downtime_auto, name='check_for_downtime_auto'),
    path('fp09/downtime_fromline', downtime_fromline, name="downtime_fromline"),
    path('fp09/get_fp09_downtime_fromline', get_fp09_downtime_fromline, name="get_fp09_downtime_fromline"),
    path('fp09/utils/split_downtimes', split_downtimes, name='split_downtimes'),
    path('fp09/utils/type_details', type_details, name='type_details'),
    path('fp09/get_fp09_alarms_sum', get_fp09_alarms_sum, name='get_fp09_alarms_sum'),
    path('fp09/get_fp09_produced_partnumber', get_fp09_produced_partnumber, name='get_fp09_produced_partnumber'),
    path('fp09/utils/get_stop_line_alarms', get_stop_line_alarms, name='get_stop_line_alarms'),
    path('fp09/utils/counter', counter, name='counter'),
]