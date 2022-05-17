from django.urls import path
from .views import accidents_home, form_nearmiss, form_injury, show_accidents, get_worker_details, process, revert, delete_picture, accidents_overview, store_data_to_db, add_corrective_measure_for_accident, add_corrective_measure_for_nearmiss


urlpatterns = [
    path('accidents', accidents_home, name='accidents_home'),
    path('accidents/form_nearmiss', form_nearmiss, name='form_nearmiss'),
    path('accidents/form_nearmiss/<int:nearmiss_id>', form_nearmiss, name='form_nearmiss'),
    path('accidents/form_injury', form_injury, name='form_injury'),
    path('accidents/form_injury/<int:accident_id>', form_injury, name='form_injury'),
    path('accidents/show_accidents', show_accidents, name='show_accidents'),
    path('accidents/get_worker_details', get_worker_details, name='get_worker_details'),
    path('accidents/process', process, name='process'),
    path('accidents/revert', revert, name='revert'),
    path('accidents/delete_picture', delete_picture, name='delete_picture'),
    path('accidents/overview', accidents_overview, name='accidents_overview'),
    path('accidents/store_data_to_db', store_data_to_db, name='store_data_to_db'),
    path('accidents/add_corrective_measure_for_accident/<int:accident_id>', add_corrective_measure_for_accident, name='add_corrective_measure_for_accident'),
    path('accidents/add_corrective_measure_for_nearmiss/<int:nearmiss_id>', add_corrective_measure_for_nearmiss, name='add_corrective_measure_for_nearmiss'),
]