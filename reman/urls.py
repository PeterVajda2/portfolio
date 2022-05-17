from django.urls import path
from .views import extract_materials, r_materials, q3, orders, report_orders, visualize_cc, visualize_yfcorer, report_yfcorer, period_setter, report_disassembly, visualize_fg, report_recondition, get_midstep_materials, order_story

urlpatterns = [
    path('reman/utils/visualize_yfcorer', visualize_yfcorer, name='visualize_yfcorer'),
    path('reman/utils/extract_materials', extract_materials, name='extract_materials'),
    path('reman/utils/r_materials', r_materials, name='r_materials'),
    path('reman/utils/q3', q3, name='q3'),
    path('reman/utils/orders', orders, name='orders'),
    path('reman/utils/report_orders', report_orders, name='report_orders'),
    path('reman/utils/report_yfcorer', report_yfcorer, name='report_yfcorer'),
    path('reman/utils/report_disassembly', report_disassembly, name='report_disassembly'),
    path('reman/utils/report_recondition', report_recondition, name='report_recondition'),
    path('reman/utils/visualize_cc', visualize_cc, name='visualize_cc'),
    path('reman/utils/visualize_fg', visualize_fg, name='visualize_fg'),
    path('reman/utils/period_setter', period_setter, name='period_setter'),
    path('reman/utils/get_midstep_materials', get_midstep_materials, name='get_midstep_materials'),
    path('reman/order_story', order_story, name='order_story')
]
