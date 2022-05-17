from django.urls import path

from thingworx.views import shift_factor
from .views import apo_comparison, shift_factor, sap_robot, update_robot_data


urlpatterns = [
    path('shift_factor/apo_comparison', apo_comparison, name="apo_comparison"),
    path('shift_factor/shift_factor', shift_factor, name="shift_factor"),
    path('shift_factor/update_robot_data', update_robot_data, name="update_robot_data"),
    path('sap_robot', sap_robot, name="sap_robot")
]