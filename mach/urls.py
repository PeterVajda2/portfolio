from django.urls import path
from .views import mach_operator_screen, split_downtimes, show_reports


app_name = "mach"

urlpatterns = [
    path('mach/operator/<str:station>', mach_operator_screen, name="mach_operator_screen"),
    path('mach/split_downtimes', split_downtimes, name="split_downtimes"),
    path('mach/reports', show_reports, name="show_reports"),
]