from django.urls import path
from .views import ksb1, ke5z, salesbook_actual_budget_split_calculation, mop_flexed_budget_month_calculation, salesbook_actual_calculation, outlook_sales_estimation, outlook_sales_actual, MOP_outlook_months_recalc, MOP_flexed_months_recalc, Outlook_Actual_recalc, outlook_calculate_all, Outlook_Outlook_recalc, Outlook_Budget_recalc, salesbook_budget_calculation, Budget_Outlook_Flexed_recalc, Budget_Budget_recalc, Budget_Flexed_Budget_recalc, Actual_Costbook_recalc, get_sql_query, get_connection_string, get_sql_query_general, prepare_manager_report, Budget_Flexed_Costbook_recalc, Budget_Costbook_recalc, outlook_mop_monthly


urlpatterns = [
    path('controlling/ksb1', ksb1, name="ksb1"),
    path('controlling/ke5z', ke5z, name="ke5z"),
    path('controlling/salesbook_actual_budget_split_calculation', salesbook_actual_budget_split_calculation, name="salesbook_actual_budget_split_calculation"),
    path('controlling/mop_flexed_budget_month_calculation', mop_flexed_budget_month_calculation, name="mop_flexed_budget_month_calculation"),
    path('controlling/salesbook_actual_calculation', salesbook_actual_calculation, name="salesbook_actual_calculation"),
    path('controlling/outlook_sales_estimation', outlook_sales_estimation, name="outlook_sales_estimation"),
    path('controlling/outlook_sales_actual', outlook_sales_actual, name="outlook_sales_actual"),
    path('controlling/MOP_outlook_months_recalc', MOP_outlook_months_recalc, name="MOP_outlook_months_recalc"),
    path('controlling/MOP_flexed_months_recalc', MOP_flexed_months_recalc, name="MOP_flexed_months_recalc"),
    path('controlling/Outlook_Actual_recalc', Outlook_Actual_recalc, name="Outlook_Actual_recalc"),
    path('controlling/Outlook_Outlook_recalc', Outlook_Outlook_recalc, name="Outlook_Outlook_recalc"),
    path('controlling/Outlook_Budget_recalc', Outlook_Budget_recalc, name="Outlook_Budget_recalc"),
    path('controlling/outlook_calculate_all', outlook_calculate_all, name="outlook_calculate_all"),
    path('controlling/salesbook_budget_calculation', salesbook_budget_calculation, name="salesbook_budget_calculation"),
    path('controlling/Budget_Outlook_Flexed_recalc', Budget_Outlook_Flexed_recalc, name="Budget_Outlook_Flexed_recalc"),
    path('controlling/Budget_Budget_recalc', Budget_Budget_recalc, name="Budget_Budget_recalc"),
    path('controlling/Budget_Flexed_Budget_recalc', Budget_Flexed_Budget_recalc, name="Budget_Flexed_Budget_recalc"),
    path('controlling/Budget_Flexed_Costbook_recalc', Budget_Flexed_Costbook_recalc, name="Budget_Flexed_Costbook_recalc"),
    path('controlling/Budget_Costbook_recalc', Budget_Costbook_recalc, name="Budget_Costbook_recalc"),
    path('controlling/Actual_Costbook_recalc', Actual_Costbook_recalc, name="Actual_Costbook_recalc"),
    path('controlling/get_sql_query', get_sql_query, name="get_sql_query"),
    path('controlling/get_connection_string', get_connection_string, name="get_connection_string"),
    path('controlling/get_sql_query_general', get_sql_query_general, name="get_sql_query_general"),
    path('controlling/outlook_mop_monthly', outlook_mop_monthly, name="outlook_mop_monthly"),
    path('controlling/prepare_manager_report', prepare_manager_report, name="prepare_manager_report"),
]