from django.urls import path
from .views import add_available, show_calendar, make_request, transfer_from_offer, transfer_from_request, show_assignments, edit_assignments, show_offers, show_requests, employees, employee_details
from .views import cancel_offer, dashboard, agree_to_cancel, decline_to_cancel, make_request_to_cancel_assignment, cancel_request, visuals, notifications_switch, help, reports, export_controlling, edit_workers

urlpatterns = [
    path('burza', show_calendar, name='burza'),
    path('burza/add_offer', add_available, name='add_available'),
    path('burza/add_offer/<int:selected_year>/<int:selected_month>/<int:selected_day>', add_available, name='add'),
    path('burza/show_calendar/<int:selected_year>/<int:selected_month>', show_calendar, name='show'),
    path('burza/show_calendar/', show_calendar, name='show'),
    path('burza/make_request', make_request, name='make_request'),
    path('burza/make_request/<int:selected_year>/<int:selected_month>/<int:selected_day>', make_request, name='make_request'),
    path('burza/transfer_from_offer/<int:offer_id>/', transfer_from_offer, name='transfer_from_offer'),
    path('burza/transfer_from_request/<int:request_id>', transfer_from_request, name='transfer_from_request'),
    path('burza/show_assignments', show_assignments, name='show_assignments'),
    path('burza/show_offers', show_offers, name='show_offers'),
    path('burza/show_requests', show_requests, name='show_requests'),
    path('burza/edit_assignments', edit_assignments, name='edit_assignments'),
    path('burza/employees', employees, name='employees'),
    path('burza/employee_details/<int:personal_number>', employee_details, name='employee_details'),
    path('burza/employee_details/cancel_offer/<int:offer_id>/', cancel_offer, name='cancel_offer'),
    path('burza/employee_details/cancel_request/<int:request_id>/', cancel_request, name='cancel_request'),
    path('burza/dashboard', dashboard, name='dashboard'),
    path('burza/pending_request/<int:pending_request_id>/agree/', agree_to_cancel, name='agree_to_cancel'),
    path('burza/pending_request/<int:pending_request_id>/decline/', decline_to_cancel, name='decline_to_cancel'),
    path('burza/employee_details/make_request_to_cancel_assignment/<int:assignment_id>/', make_request_to_cancel_assignment, name='make_request_to_cancel_assignment'),
    path('burza/visuals/', visuals, name='visuals'),
    path('burza/notifications_switch/', notifications_switch, name='notifications_switch'),
    path('burza/help/', help, name='help'),
    path('burza/reports/', reports, name='reports'),
    path('burza/edit_workers', edit_workers, name='edit_workers'),
    path('burza/export_controlling', export_controlling, name='export_controlling'),
]

