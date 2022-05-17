from django.urls import path
from .views import admin_view,  show_employees, add_employee, remove_employee, edit_employee, create_questionnaire, edit_questionnaire, check_questionnaire, evaluate_questionnaire, distribute_questionnaire, my_questionnaires, fill_in_questionnaire, edit_interviewees, edit_filled_in_questionnaire, validate_survey_name, ranged_answers, show_questionnaire, edit_questionnaire_list, delete_range, my_questionnaires_list, change_answer, questionnaire_results, questionnaire_results_questionnaire, questionnaire_results_questionnaire_charts, employee_upload, homepage_view, update_evaluators, fill_in_questionnaire_devel


urlpatterns = [
    path('engagement/admin', admin_view, name='admin_view'),
    path('engagement', homepage_view, name='homepage_view'),
    path('engagement/admin/employees', show_employees, name='show_employees'),
    path('engagement/admin/employee_upload', employee_upload, name='employee_upload'),
    path('engagement/admin/show_questionnaire/<int:questionnaire_id>', show_questionnaire, name='show_questionnaire'),
    path('engagement/admin/employees/add_employee', add_employee, name='add_employee'),
    path('engagement/admin/employees/remove_employee/<int:employee_id>', remove_employee, name='remove_employee'),
    path('engagement/admin/employees/edit_employee/<int:employee_id>', edit_employee, name='edit_employee'),
    path('engagement/admin/create_questionnaire', create_questionnaire, name='create_questionnaire'),
    path('engagement/admin/edit_questionnaire/<int:questionnaire_id>', edit_questionnaire, name='edit_questionnaire'),
    path('engagement/admin/edit_questionnaire_list', edit_questionnaire_list, name='edit_questionnaire_list'),
    path('engagement/admin/ranged_answers', ranged_answers, name='ranged_answers'),
    path('engagement/admin/delete_ranged_answer', delete_range, name='delete_range'),
    path('engagement/admin/check_questionnaire/<int:questionnaire_id>', check_questionnaire, name='check_questionnaire'),
    path('engagement/admin/evaluate_questionnaire/<int:questionnaire_id>', evaluate_questionnaire, name='evaluate_questionnaire'),
    path('engagement/admin/distribute_questionnaire', distribute_questionnaire, name='distribute_questionnaire'),
    path('engagement/my_questionnaires_list', my_questionnaires_list, name='my_questionnaires_list'),
    path('engagement/my_questionnaires/<int:questionnairetemplate_id>', my_questionnaires, name='my_questionnaires'),
    path('engagement/fill_in_questionnaire/<int:questionnaire_id>', fill_in_questionnaire, name='fill_in_questionnaire'),
    path('engagement/fill_in_questionnaire_devel/<int:questionnaire_id>', fill_in_questionnaire_devel, name='fill_in_questionnaire_devel'),
    path('engagement/edit_interviewees', edit_interviewees, name='edit_interviewees'),
    path('engagement/edit_filled_in_questionnaire/<int:questionnaire_id>', edit_filled_in_questionnaire, name='edit_filled_in_questionnaire'),
    path('engagement/validate_survey_name', validate_survey_name, name='validate_survey_name'),
    path('engagement/change_answer/<int:questionnaire_id>/<int:question_id>', change_answer, name='change_answer'),
    path('engagement/admin/questionnaire_results', questionnaire_results, name='questionnaire_results'),
    path('engagement/admin/questionnaire_results/<int:questionnaire_id>', questionnaire_results_questionnaire, name='questionnaire_results_questionnaire'),
    path('engagement/admin/questionnaire_results/charts/<int:questionnaire_id>', questionnaire_results_questionnaire_charts, name='questionnaire_results_questionnaire_charts'),
    path('engagement/admin/update_evaluators', update_evaluators, name='update_evaluators'),
]
