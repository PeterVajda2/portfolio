from django.urls import path
from .views import add_action, show_single_action, show_actions, edit_action, edit_multiple_actions, show_charts, recalcActualYearSavings, recalcMonthlySavings, show_news, read_news, doi_change_agree

urlpatterns = [
    path('covcap', show_actions, name='show_all'),
    path('covcap/add_action', add_action, name='add_action'),
    path('covcap/show_action/<int:action_id>', show_single_action, name='show_action'),
    path('covcap/edit_action/<int:action_id>', edit_action, name='edit_action'),
    path('covcap/edit_multiple_actions>', edit_multiple_actions, name='edit_multiple_actions'),
    path('covcap/show_charts', show_charts, name='show_charts'),
    path('covcap/show_charts/<str:currency>', show_charts, name='show_charts'),
    path('covcap/add_action/<str:currency>', add_action, name='add_action'),
    path('covcap/edit_action/<int:action_id>/<str:currency>', edit_action, name='edit_action'),
    path('covcap/news', show_news, name='show_news'),
    path('covcap/read_news', read_news, name='read_news'),
    path('covcap/recalcYear', recalcActualYearSavings),
    path('covcap/recalcMonth', recalcMonthlySavings),
    path('covcap/doi_change_agree/<int:action_id>/<int:doi>', doi_change_agree, name='doi_change_agree'),
    path('covcap/<str:currency>', show_actions, name='covcap'),
]
