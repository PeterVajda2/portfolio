from django.urls import path
from .views import index, show_parts, upload_spare_parts_list, check_if_part_exists, upload_parts, upload_parts_to_database, save_parts, add_line, remove_line, remove_parts_from_database, show_parts_from_line, delete_line, edit_columns

urlpatterns = [
    path('maintenance', index, name='index'),
    path('maintenance/show_parts', show_parts, name='show_parts'),
    path('maintenance/add_line', add_line, name='add_line'),
    path('maintenance/delete_line', delete_line, name='delete_line'),
    path('maintenance/remove_line', remove_line, name='remove_line'),
    path('maintenance/show_parts_from_line', show_parts_from_line, name='show_parts_from_line'),
    path('maintenance/upload_parts', upload_parts, name='upload_parts'),
    path('maintenance/upload_spare_parts_list', upload_spare_parts_list, name='upload_spare_parts_list'),
    path('maintenance/edit_columns', edit_columns, name='edit_columns'),
    path('maintenance/utils/check_if_part_exists', check_if_part_exists, name='check_if_part_exists'),
    path('maintenance/utils/upload_parts_to_database', upload_parts_to_database, name='upload_parts_to_database'),
    path('maintenance/utils/save_parts', save_parts, name='save_parts'),
    path('maintenance/utils/remove_parts_from_database', remove_parts_from_database, name='remove_parts_from_database'),
]
