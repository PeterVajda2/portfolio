from django.urls import path
from .views import excel_to_db, sendmail

urlpatterns = [
    path('quality/excel_to_db', excel_to_db, name='excel_to_db'),
    path('quality/sendmail', sendmail, name='sendmail'),
]
