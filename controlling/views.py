from django.shortcuts import render, HttpResponse
from .models import Ksb1, Ke5z, MM1, MM2, MM4, MM5, MM6, MM7, Flexrates, Ke5z_updated, Salesbook_Budget, Salesbook_Actual, Salesbook_Actual_Budget_Split, MOP, Sales_From_Munich, Outlook_Sales_Actual, Outlook_Sales_Estimation, MOP_Outlook, Outlook_MOP_Monthly, Outlook_Corrections, Outlook_Actual, Outlook_Outlook, Outlook_Budget, Budget_Outlook_Flexed, Budget_Flexed_Budget, Budget_Budget, Actual_Costbook, Closing_Corrections, Budget_Costbook, Manager, Manager_Report, Budget_Flexed_Costbook, Ke5z_reman, Ke5z_updated_reman, Ksb1_reman, Ke5z_updated_temp, Ke5z_updated_reman_temp
from django.db.models import Sum
from django.db import connection

from email.message import EmailMessage
import smtplib
from django.views.decorators.csrf import csrf_exempt
import ldap
from django.db import connection


def Actual_Costbook_recalc(request=None, month=None, year=None):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
    else:
        if not year:
            year = 2021

    if not month:
        for i in range(1,13):
            attributes = {}
            attributes['gross_sales_merchandized_3p'] = (Ke5z_updated.objects.filter(functional_area="SA01", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SA01").to_be_considered or 0)
            attributes['gross_sales_merchandized_ic'] = (Ke5z_updated.objects.filter(functional_area="SA02", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SA02").to_be_considered or 0)
            attributes['gross_sales_merchandized'] = attributes['gross_sales_merchandized_3p'] + attributes['gross_sales_merchandized_ic']
            attributes['gross_sales_own_production_3p'] = (Ke5z_updated.objects.filter(functional_area="SA03", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SA03").to_be_considered or 0)
            attributes['gross_sales_own_production_ic'] = (Ke5z_updated.objects.filter(functional_area="SA04", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SA04").to_be_considered or 0)
            attributes['gross_sales_own_production'] = attributes['gross_sales_own_production_3p'] + attributes['gross_sales_own_production_ic']
            attributes['gross_sales'] = attributes['gross_sales_merchandized'] + attributes['gross_sales_own_production']
            attributes['customer_discounts'] = (Ke5z_updated.objects.filter(functional_area="OR11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="OR11").to_be_considered or 0)
            attributes['pricing_differences'] = (Ke5z_updated.objects.filter(functional_area="OR12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="OR12").to_be_considered or 0)
            attributes['royalties_licences_3p'] = (Ke5z_updated.objects.filter(functional_area="OR13", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="OR13").to_be_considered or 0)
            attributes['core_revenues'] = (Ke5z_updated.objects.filter(functional_area="OR14", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="OR14").to_be_considered or 0)
            attributes['income_from_scrap'] = (Ke5z_updated.objects.filter(functional_area="OR15", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="OR15").to_be_considered or 0)
            attributes['other_revenues'] = attributes['customer_discounts'] + attributes['pricing_differences'] + attributes['royalties_licences_3p'] + attributes['core_revenues'] + attributes['income_from_scrap']
            attributes['other_revenues_in_of_gross_sales'] = (attributes['other_revenues'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['net_sales'] = attributes['other_revenues'] + attributes['gross_sales']
            attributes['increase_decrease_of_finished_goods_wip_hk_1'] = (Ke5z_updated.objects.filter(functional_area="IN11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="IN11").to_be_considered or 0)
            attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1'] = (Ke5z_updated.objects.filter(functional_area="IN12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="IN12").to_be_considered or 0)
            attributes['inventory_change'] = attributes['increase_decrease_of_finished_goods_wip_hk_1'] + attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1']
            attributes['self_constructed_assets'] = (Ke5z_updated.objects.filter(functional_area="OW11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="OW11").to_be_considered or 0)
            attributes['own_work_capitalized'] = attributes['self_constructed_assets']
            attributes['total_operating_performance'] = attributes['own_work_capitalized'] + attributes['inventory_change'] + attributes['net_sales']
            attributes['direct_production_material'] = (Ke5z_updated.objects.filter(functional_area="MD11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MD11").to_be_considered or 0)
            attributes['merchandise_parts'] = (Ke5z_updated.objects.filter(functional_area="MD12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MD12").to_be_considered or 0)
            attributes['sub_contracting'] = (Ke5z_updated.objects.filter(functional_area="MD13", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MD13").to_be_considered or 0)
            attributes['excess_obsolete_stock'] = (Ke5z_updated.objects.filter(functional_area="MD14", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MD14").to_be_considered or 0)
            attributes['scrap'] = (Ke5z_updated.objects.filter(functional_area="MD15", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MD15").to_be_considered or 0)
            attributes['increase_decrease_of_finished_goods_wip'] = (Ke5z_updated.objects.filter(functional_area="MD16", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MD16").to_be_considered or 0)
            attributes['target'] = (Ke5z_updated.objects.filter(functional_area="MD17", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MD17").to_be_considered or 0)
            attributes['inventory_shrink_and_revaluations'] = (Ke5z_updated.objects.filter(functional_area="MD18", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MD18").to_be_considered or 0)
            attributes['material_direct'] = attributes['direct_production_material'] + attributes['merchandise_parts'] + attributes['sub_contracting'] + attributes['excess_obsolete_stock'] + attributes['scrap'] + attributes['increase_decrease_of_finished_goods_wip'] + attributes['target'] + attributes['inventory_shrink_and_revaluations']
            attributes['material_direct_in_of_gross_sales'] = (attributes['material_direct'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['material_direct_in_of_operating_performance'] = (attributes['material_direct'] / attributes['total_operating_performance']) if attributes['total_operating_performance'] else 0
            attributes['purchase_mat_di'] = (Ke5z_updated.objects.filter(functional_area="MO11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MO11").to_be_considered or 0)
            attributes['tooling_supplier'] = (Ke5z_updated.objects.filter(functional_area="MO12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MO12").to_be_considered or 0)
            attributes['procurement'] = (Ke5z_updated.objects.filter(functional_area="MO13", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MO13").to_be_considered or 0)
            attributes['freight_in'] = (Ke5z_updated.objects.filter(functional_area="MO14", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MO14").to_be_considered or 0)
            attributes['inbound_logistic'] = (Ke5z_updated.objects.filter(functional_area="MO15", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MO15").to_be_considered or 0)
            attributes['quality_supplier'] = (Ke5z_updated.objects.filter(functional_area="MO16", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MO16").to_be_considered or 0)
            attributes['target_poc'] = (Ke5z_updated.objects.filter(functional_area="MO17", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MO17").to_be_considered or 0)
            attributes['target_gen_costs'] = (Ke5z_updated.objects.filter(functional_area="MO18", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="MO18").to_be_considered or 0)
            attributes['material_overhead'] = attributes['target_gen_costs'] + attributes['target_poc'] + attributes['quality_supplier'] + attributes['inbound_logistic'] + attributes['freight_in'] + attributes['procurement'] + attributes['tooling_supplier'] + attributes['purchase_mat_di']
            attributes['material_overhead_in_of_gross_sales'] = (attributes['material_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['material_overhead_in_of_net_sales'] = (attributes['material_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['assembly_direct'] = (Ke5z_updated.objects.filter(functional_area="WD11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WD11").to_be_considered or 0)
            attributes['machining_direct'] = (Ke5z_updated.objects.filter(functional_area="WD12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WD12").to_be_considered or 0)
            attributes['pre_assembly_direct'] = (Ke5z_updated.objects.filter(functional_area="WD13", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WD13").to_be_considered or 0)
            attributes['pre_machining_direct'] = (Ke5z_updated.objects.filter(functional_area="WD14", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WD14").to_be_considered or 0)
            attributes['surface_treatment_direct'] = (Ke5z_updated.objects.filter(functional_area="WD15", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WD15").to_be_considered or 0)
            attributes['other_direct_production_cost_centers_direct'] = (Ke5z_updated.objects.filter(functional_area="WD16", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WD16").to_be_considered or 0)
            attributes['remanufacturing_direct'] = (Ke5z_updated.objects.filter(functional_area="WD17", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WD17").to_be_considered or 0)
            attributes['welding_direct_production_direct'] = (Ke5z_updated.objects.filter(functional_area="WD18", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WD18").to_be_considered or 0)
            attributes['target_poc_direct'] = (Ke5z_updated.objects.filter(functional_area="WD19", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WD19").to_be_considered or 0)
            attributes['direct_labour'] = attributes['target_poc_direct'] + attributes['welding_direct_production_direct'] + attributes['remanufacturing_direct'] + attributes['other_direct_production_cost_centers_direct'] + attributes['surface_treatment_direct'] + attributes['pre_machining_direct'] + attributes['pre_assembly_direct'] + attributes['machining_direct'] + attributes['assembly_direct']
            attributes['direct_labour_in_of_gross_sales'] = (attributes['direct_labour'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['direct_labour_in_of_net_sales'] = (attributes['direct_labour'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['direct_labour_in_of_sales_own_production'] = (attributes['direct_labour'] / attributes['gross_sales_own_production']) if attributes['gross_sales_own_production'] else 0
            attributes['assembly_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO11").to_be_considered or 0)
            attributes['machining_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO12").to_be_considered or 0)
            attributes['pre_assembly_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO13", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO13").to_be_considered or 0)
            attributes['pre_machining_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO14", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO14").to_be_considered or 0)
            attributes['surface_treatment_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO15", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO15").to_be_considered or 0)
            attributes['other_direct_production_cost_centers_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO16", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO16").to_be_considered or 0)
            attributes['remanufacturing_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO17", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO17").to_be_considered or 0)
            attributes['welding_direct_production_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO18", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO18").to_be_considered or 0)
            attributes['production_supply'] = (Ke5z_updated.objects.filter(functional_area="WO19", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO19").to_be_considered or 0)
            attributes['energy_utilities'] = (Ke5z_updated.objects.filter(functional_area="WO20", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO20").to_be_considered or 0)
            attributes['production_planning'] = (Ke5z_updated.objects.filter(functional_area="WO21", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO21").to_be_considered or 0)
            attributes['facility_costs'] = (Ke5z_updated.objects.filter(functional_area="WO22", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO22").to_be_considered or 0)
            attributes['maintenance_dept'] = (Ke5z_updated.objects.filter(functional_area="WO23", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO23").to_be_considered or 0)
            attributes['production_eng'] = (Ke5z_updated.objects.filter(functional_area="WO24", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO24").to_be_considered or 0)
            attributes['production_management'] = (Ke5z_updated.objects.filter(functional_area="WO25", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO25").to_be_considered or 0)
            attributes['quality_production'] = (Ke5z_updated.objects.filter(functional_area="WO26", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO26").to_be_considered or 0)
            attributes['quality_general'] = (Ke5z_updated.objects.filter(functional_area="WO27", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO27").to_be_considered or 0)
            attributes['purchasing_indirect_material'] = (Ke5z_updated.objects.filter(functional_area="WO28", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO28").to_be_considered or 0)
            attributes['warranty_plant'] = (Ke5z_updated.objects.filter(functional_area="WO29", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO29").to_be_considered or 0)
            attributes['target_poc_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO30", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO30").to_be_considered or 0)
            attributes['target_gen_costs'] = (Ke5z_updated.objects.filter(functional_area="WO31", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="WO31").to_be_considered or 0)
            attributes['manufacturing_overhead'] = attributes['target_gen_costs'] + attributes['target_poc_overhead'] + attributes['warranty_plant'] + attributes['purchasing_indirect_material'] + attributes['quality_general'] + attributes['quality_production'] + attributes['production_management'] + attributes['production_eng'] + attributes['maintenance_dept'] + attributes['facility_costs'] + attributes['production_planning'] + attributes['energy_utilities'] + attributes['production_supply'] + attributes['welding_direct_production_overhead']  + attributes['remanufacturing_overhead'] + attributes['other_direct_production_cost_centers_overhead'] + attributes['surface_treatment_overhead'] + attributes['pre_machining_overhead'] + attributes['pre_assembly_overhead'] + attributes['machining_overhead'] + attributes['assembly_overhead']
            attributes['manufacturing_overhead_in_of_gross_sales'] = (attributes['manufacturing_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['manufacturing_overhead_in_of_net_sales'] = (attributes['manufacturing_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['hk_1'] = attributes['manufacturing_overhead'] + attributes['direct_labour'] + attributes['material_overhead'] + attributes['material_direct']
            attributes['gross_profit_operating_performance'] = attributes['hk_1'] + attributes['total_operating_performance']
            attributes['gross_profit_in_of_gross_sales'] = (attributes['gross_profit_operating_performance'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['gross_profit_after_other_rev_in_of_net_sales'] = (attributes['gross_profit_operating_performance'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['general_management'] = (Ke5z_updated.objects.filter(functional_area="AD11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD11").to_be_considered or 0)
            attributes['plant_admin'] = (Ke5z_updated.objects.filter(functional_area="AD12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD12").to_be_considered or 0)
            attributes['central_functions'] = (Ke5z_updated.objects.filter(functional_area="AD13", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD13").to_be_considered or 0)
            attributes['central_function_indirect_purchasing'] = (Ke5z_updated.objects.filter(functional_area="AD14", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD14").to_be_considered or 0)
            attributes['information_technology'] = (Ke5z_updated.objects.filter(functional_area="AD15", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD15").to_be_considered or 0)
            attributes['admin_facility_costs_energy'] = (Ke5z_updated.objects.filter(functional_area="AD16", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD16").to_be_considered or 0)
            attributes['special_projects'] = (Ke5z_updated.objects.filter(functional_area="AD17", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD17").to_be_considered or 0)
            attributes['target_poc'] = (Ke5z_updated.objects.filter(functional_area="AD18", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD18").to_be_considered or 0)
            attributes['target_gen_costs'] = (Ke5z_updated.objects.filter(functional_area="AD19", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD19").to_be_considered or 0)
            attributes['central_function_direct_purchasing'] = (Ke5z_updated.objects.filter(functional_area="AD21", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD21").to_be_considered or 0)
            attributes['central_function_industrial_engineering'] = (Ke5z_updated.objects.filter(functional_area="AD22", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD22").to_be_considered or 0)
            attributes['central_function_logistics'] = (Ke5z_updated.objects.filter(functional_area="AD23", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD23").to_be_considered or 0)
            attributes['hr'] = (Ke5z_updated.objects.filter(functional_area="AD24", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD24").to_be_considered or 0)
            attributes['plant_hr'] = (Ke5z_updated.objects.filter(functional_area="AD25", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD25").to_be_considered or 0)
            attributes['finance_controlling'] = (Ke5z_updated.objects.filter(functional_area="AD26", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD26").to_be_considered or 0)
            attributes['plant_finance_controlling'] = (Ke5z_updated.objects.filter(functional_area="AD27", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD27").to_be_considered or 0)
            attributes['central_quality_management'] = (Ke5z_updated.objects.filter(functional_area="AD28", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD28").to_be_considered or 0)
            attributes['apprenticeship_trainee_programs'] = (Ke5z_updated.objects.filter(functional_area="AD29", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD29").to_be_considered or 0)
            attributes['other_central_support_functions'] = (Ke5z_updated.objects.filter(functional_area="AD30", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD30").to_be_considered or 0)
            attributes['other_plant_support_functions'] = (Ke5z_updated.objects.filter(functional_area="AD31", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="AD31").to_be_considered or 0)
            attributes['admin'] = attributes['general_management'] + attributes['plant_admin'] + attributes['central_functions'] + attributes['central_function_indirect_purchasing'] + attributes['information_technology'] + attributes['admin_facility_costs_energy'] + attributes['special_projects'] + attributes['target_poc'] + attributes['target_gen_costs'] + attributes['central_function_direct_purchasing'] + attributes['central_function_industrial_engineering'] + attributes['central_function_logistics'] + attributes['hr'] + attributes['plant_hr'] + attributes['finance_controlling'] + attributes['plant_finance_controlling'] + attributes['central_quality_management'] + attributes['apprenticeship_trainee_programs'] + attributes['other_central_support_functions'] + attributes['other_plant_support_functions']
            attributes['admin_in_of_net_sales'] = (attributes['admin'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['customer_service_plant'] = (Ke5z_updated.objects.filter(functional_area="SM11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM11").to_be_considered or 0)
            attributes['central_customer_service'] = (Ke5z_updated.objects.filter(functional_area="SM12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM12").to_be_considered or 0)
            attributes['marketing'] = (Ke5z_updated.objects.filter(functional_area="SM13", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM13").to_be_considered or 0)
            attributes['sales_force'] = (Ke5z_updated.objects.filter(functional_area="SM14", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM14").to_be_considered or 0)
            attributes['outbound_logistic_plant'] = (Ke5z_updated.objects.filter(functional_area="SM15", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM15").to_be_considered or 0)
            attributes['sales_logistic'] = (Ke5z_updated.objects.filter(functional_area="SM16", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM16").to_be_considered or 0)
            attributes['freight_out'] = (Ke5z_updated.objects.filter(functional_area="SM17", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM17").to_be_considered or 0)
            attributes['target_poc'] = (Ke5z_updated.objects.filter(functional_area="SM18", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM18").to_be_considered or 0)
            attributes['target_gen_costs'] = (Ke5z_updated.objects.filter(functional_area="SM19", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM19").to_be_considered or 0)
            attributes['sales_facility_costs_energy'] = (Ke5z_updated.objects.filter(functional_area="SM26", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM26").to_be_considered or 0)
            attributes['other_sales_costs'] = (Ke5z_updated.objects.filter(functional_area="SM27", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM27").to_be_considered or 0)
            attributes['sales_income'] = (Ke5z_updated.objects.filter(functional_area="SM28", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM28").to_be_considered or 0)
            attributes['sales_managment'] = (Ke5z_updated.objects.filter(functional_area="SM29", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="SM29").to_be_considered or 0)
            attributes['sales_marketing'] = attributes['sales_managment'] + attributes['sales_income'] + attributes['other_sales_costs'] + attributes['sales_facility_costs_energy'] + attributes['target_gen_costs'] + attributes['target_poc'] + attributes['freight_out'] + attributes['sales_logistic'] + attributes['outbound_logistic_plant'] + attributes['sales_force'] + attributes['marketing'] + attributes['central_customer_service'] + attributes['customer_service_plant']
            attributes['sales_marketing_in_of_net_sales'] = (attributes['sales_marketing'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['general_rd_engineering_management_admin'] = (Ke5z_updated.objects.filter(functional_area="RD10", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="RD10").to_be_considered or 0)
            attributes['advanced_eng_innovation_mgt'] = (Ke5z_updated.objects.filter(functional_area="RD11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="RD11").to_be_considered or 0)
            attributes['engineering'] = (Ke5z_updated.objects.filter(functional_area="RD12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="RD12").to_be_considered or 0)
            attributes['platform_engineering_service'] = (Ke5z_updated.objects.filter(functional_area="RD13", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="RD13").to_be_considered or 0)
            attributes['rd_facility_costs_energy'] = (Ke5z_updated.objects.filter(functional_area="RD14", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="RD14").to_be_considered or 0)
            attributes['rd_tooling'] = (Ke5z_updated.objects.filter(functional_area="RD15", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="RD15").to_be_considered or 0)
            attributes['rd_system_engineering'] = (Ke5z_updated.objects.filter(functional_area="RD16", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="RD16").to_be_considered or 0)
            attributes['rd_target_gc'] = (Ke5z_updated.objects.filter(functional_area="RD17", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="RD17").to_be_considered or 0)
            attributes['product_management'] = (Ke5z_updated.objects.filter(functional_area="RD24", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="RD24").to_be_considered or 0)
            attributes['rd'] = attributes['product_management'] + attributes['rd_target_gc'] + attributes['rd_system_engineering'] + attributes['rd_tooling'] + attributes['rd_facility_costs_energy'] + attributes['platform_engineering_service'] + attributes['engineering'] + attributes['advanced_eng_innovation_mgt'] + attributes['general_rd_engineering_management_admin']
            attributes['rd_in_of_net_sales'] = (attributes['rd'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['primary_result'] = attributes['rd'] + attributes['sales_marketing'] + attributes['admin'] + attributes['gross_profit_operating_performance']
            attributes['primary_result_in_of_net_sales'] = (attributes['primary_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['intercompany_charges'] = (Ke5z_updated.objects.filter(functional_area="IC11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="IC11").to_be_considered or 0)
            attributes['ic_hq'] = attributes['intercompany_charges']
            attributes['ic_charges_in_of_net_sales'] = (attributes['ic_hq'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['other_plant'] = (Ke5z_updated.objects.filter(functional_area="OT01", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="OT01").to_be_considered or 0)
            attributes['other_general_costs'] = (Ke5z_updated.objects.filter(functional_area="OT02", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="OT02").to_be_considered or 0)
            attributes['customer_quality_campaigns'] = (Ke5z_updated.objects.filter(functional_area="OT03", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="OT03").to_be_considered or 0)
            attributes['other'] = attributes['customer_quality_campaigns'] + attributes['other_general_costs'] + attributes['other_plant']
            attributes['other_in_of_net_sales']  = (attributes['other'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['ebit'] = attributes['primary_result'] + attributes['other']
            attributes['ebit_in_of_net_sales'] = (attributes['ebit'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['interest_result'] = (Ke5z_updated.objects.filter(functional_area="FR11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="FR11").to_be_considered or 0)
            attributes['income_from_investments'] = (Ke5z_updated.objects.filter(functional_area="FR12", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="FR12").to_be_considered or 0)
            attributes['financial_result'] = attributes['interest_result'] + attributes['income_from_investments']
            attributes['financial_result_in_of_net_sales'] = (attributes['financial_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['pb_t'] = attributes['ebit'] + attributes['financial_result']
            attributes['ros_in'] = (attributes['pb_t'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['extraordinary_result'] = (Ke5z_updated.objects.filter(functional_area="EO11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="EO11").to_be_considered or 0)
            attributes['extraordinary_result_2'] = attributes['extraordinary_result']
            attributes['profit_loss_transfer'] = (Ke5z_updated.objects.filter(functional_area="PL11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="PL11").to_be_considered or 0)
            attributes['profit_loss_transfer_2'] = attributes['profit_loss_transfer']
            attributes['income_tax'] = (Ke5z_updated.objects.filter(functional_area="TX11", record_type=0, posting_period=i, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=i, year=year, functional_area="TX11").to_be_considered or 0)
            attributes['income_tax_2'] = attributes['income_tax']
            attributes['company_result'] = attributes['pb_t'] + attributes['extraordinary_result_2'] + attributes['profit_loss_transfer_2'] + attributes['income_tax_2']
            attributes['own_production_operating_performance'] = attributes['gross_sales_own_production'] + attributes['inventory_change']

            Actual_Costbook.objects.update_or_create(month=i, year=year, defaults=attributes)
    else:
        attributes = {}
        attributes['gross_sales_merchandized_3p'] = (Ke5z_updated.objects.filter(functional_area="SA01", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SA01").to_be_considered or 0)
        attributes['gross_sales_merchandized_ic'] = (Ke5z_updated.objects.filter(functional_area="SA02", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SA02").to_be_considered or 0)
        attributes['gross_sales_merchandized'] = attributes['gross_sales_merchandized_3p'] + attributes['gross_sales_merchandized_ic']
        attributes['gross_sales_own_production_3p'] = (Ke5z_updated.objects.filter(functional_area="SA03", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SA03").to_be_considered or 0)
        attributes['gross_sales_own_production_ic'] = (Ke5z_updated.objects.filter(functional_area="SA04", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SA04").to_be_considered or 0)
        attributes['gross_sales_own_production'] = attributes['gross_sales_own_production_3p'] + attributes['gross_sales_own_production_ic']
        attributes['gross_sales'] = attributes['gross_sales_merchandized'] + attributes['gross_sales_own_production']
        attributes['customer_discounts'] = (Ke5z_updated.objects.filter(functional_area="OR11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="OR11").to_be_considered or 0)
        attributes['pricing_differences'] = (Ke5z_updated.objects.filter(functional_area="OR12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="OR12").to_be_considered or 0)
        attributes['royalties_licences_3p'] = (Ke5z_updated.objects.filter(functional_area="OR13", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="OR13").to_be_considered or 0)
        attributes['core_revenues'] = (Ke5z_updated.objects.filter(functional_area="OR14", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="OR14").to_be_considered or 0)
        attributes['income_from_scrap'] = (Ke5z_updated.objects.filter(functional_area="OR15", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="OR15").to_be_considered or 0)
        attributes['other_revenues'] = attributes['customer_discounts'] + attributes['pricing_differences'] + attributes['royalties_licences_3p'] + attributes['core_revenues'] + attributes['income_from_scrap']
        attributes['other_revenues_in_of_gross_sales'] = (attributes['other_revenues'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['net_sales'] = attributes['other_revenues'] + attributes['gross_sales']
        attributes['increase_decrease_of_finished_goods_wip_hk_1'] = (Ke5z_updated.objects.filter(functional_area="IN11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="IN11").to_be_considered or 0)
        attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1'] = (Ke5z_updated.objects.filter(functional_area="IN12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="IN12").to_be_considered or 0)
        attributes['inventory_change'] = attributes['increase_decrease_of_finished_goods_wip_hk_1'] + attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1']
        attributes['self_constructed_assets'] = (Ke5z_updated.objects.filter(functional_area="OW11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="OW11").to_be_considered or 0)
        attributes['own_work_capitalized'] = attributes['self_constructed_assets']
        attributes['total_operating_performance'] = attributes['own_work_capitalized'] + attributes['inventory_change'] + attributes['net_sales']
        attributes['direct_production_material'] = (Ke5z_updated.objects.filter(functional_area="MD11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MD11").to_be_considered or 0)
        attributes['merchandise_parts'] = (Ke5z_updated.objects.filter(functional_area="MD12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MD12").to_be_considered or 0)
        attributes['sub_contracting'] = (Ke5z_updated.objects.filter(functional_area="MD13", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MD13").to_be_considered or 0)
        attributes['excess_obsolete_stock'] = (Ke5z_updated.objects.filter(functional_area="MD14", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MD14").to_be_considered or 0)
        attributes['scrap'] = (Ke5z_updated.objects.filter(functional_area="MD15", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MD15").to_be_considered or 0)
        attributes['increase_decrease_of_finished_goods_wip'] = (Ke5z_updated.objects.filter(functional_area="MD16", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MD16").to_be_considered or 0)
        attributes['target'] = (Ke5z_updated.objects.filter(functional_area="MD17", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MD17").to_be_considered or 0)
        attributes['inventory_shrink_and_revaluations'] = (Ke5z_updated.objects.filter(functional_area="MD18", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MD18").to_be_considered or 0)
        attributes['material_direct'] = attributes['direct_production_material'] + attributes['merchandise_parts'] + attributes['sub_contracting'] + attributes['excess_obsolete_stock'] + attributes['scrap'] + attributes['increase_decrease_of_finished_goods_wip'] + attributes['target'] + attributes['inventory_shrink_and_revaluations']
        attributes['material_direct_in_of_gross_sales'] = (attributes['material_direct'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['material_direct_in_of_operating_performance'] = (attributes['material_direct'] / attributes['total_operating_performance']) if attributes['total_operating_performance'] else 0
        attributes['purchase_mat_di'] = (Ke5z_updated.objects.filter(functional_area="MO11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MO11").to_be_considered or 0)
        attributes['tooling_supplier'] = (Ke5z_updated.objects.filter(functional_area="MO12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MO12").to_be_considered or 0)
        attributes['procurement'] = (Ke5z_updated.objects.filter(functional_area="MO13", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MO13").to_be_considered or 0)
        attributes['freight_in'] = (Ke5z_updated.objects.filter(functional_area="MO14", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MO14").to_be_considered or 0)
        attributes['inbound_logistic'] = (Ke5z_updated.objects.filter(functional_area="MO15", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MO15").to_be_considered or 0)
        attributes['quality_supplier'] = (Ke5z_updated.objects.filter(functional_area="MO16", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MO16").to_be_considered or 0)
        attributes['target_poc'] = (Ke5z_updated.objects.filter(functional_area="MO17", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MO17").to_be_considered or 0)
        attributes['target_gen_costs'] = (Ke5z_updated.objects.filter(functional_area="MO18", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="MO18").to_be_considered or 0)
        attributes['material_overhead'] = attributes['target_gen_costs'] + attributes['target_poc'] + attributes['quality_supplier'] + attributes['inbound_logistic'] + attributes['freight_in'] + attributes['procurement'] + attributes['tooling_supplier'] + attributes['purchase_mat_di']
        attributes['material_overhead_in_of_gross_sales'] = (attributes['material_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['material_overhead_in_of_net_sales'] = (attributes['material_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['assembly_direct'] = (Ke5z_updated.objects.filter(functional_area="WD11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WD11").to_be_considered or 0)
        attributes['machining_direct'] = (Ke5z_updated.objects.filter(functional_area="WD12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WD12").to_be_considered or 0)
        attributes['pre_assembly_direct'] = (Ke5z_updated.objects.filter(functional_area="WD13", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WD13").to_be_considered or 0)
        attributes['pre_machining_direct'] = (Ke5z_updated.objects.filter(functional_area="WD14", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WD14").to_be_considered or 0)
        attributes['surface_treatment_direct'] = (Ke5z_updated.objects.filter(functional_area="WD15", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WD15").to_be_considered or 0)
        attributes['other_direct_production_cost_centers_direct'] = (Ke5z_updated.objects.filter(functional_area="WD16", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WD16").to_be_considered or 0)
        attributes['remanufacturing_direct'] = (Ke5z_updated.objects.filter(functional_area="WD17", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WD17").to_be_considered or 0)
        attributes['welding_direct_production_direct'] = (Ke5z_updated.objects.filter(functional_area="WD18", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WD18").to_be_considered or 0)
        attributes['target_poc_direct'] = (Ke5z_updated.objects.filter(functional_area="WD19", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WD19").to_be_considered or 0)
        attributes['direct_labour'] = attributes['target_poc_direct'] + attributes['welding_direct_production_direct'] + attributes['remanufacturing_direct'] + attributes['other_direct_production_cost_centers_direct'] + attributes['surface_treatment_direct'] + attributes['pre_machining_direct'] + attributes['pre_assembly_direct'] + attributes['machining_direct'] + attributes['assembly_direct']
        attributes['direct_labour_in_of_gross_sales'] = (attributes['direct_labour'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['direct_labour_in_of_net_sales'] = (attributes['direct_labour'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['direct_labour_in_of_sales_own_production'] = (attributes['direct_labour'] / attributes['gross_sales_own_production']) if attributes['gross_sales_own_production'] else 0
        attributes['assembly_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO11").to_be_considered or 0)
        attributes['machining_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO12").to_be_considered or 0)
        attributes['pre_assembly_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO13", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO13").to_be_considered or 0)
        attributes['pre_machining_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO14", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO14").to_be_considered or 0)
        attributes['surface_treatment_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO15", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO15").to_be_considered or 0)
        attributes['other_direct_production_cost_centers_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO16", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO16").to_be_considered or 0)
        attributes['remanufacturing_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO17", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO17").to_be_considered or 0)
        attributes['welding_direct_production_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO18", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO18").to_be_considered or 0)
        attributes['production_supply'] = (Ke5z_updated.objects.filter(functional_area="WO19", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO19").to_be_considered or 0)
        attributes['energy_utilities'] = (Ke5z_updated.objects.filter(functional_area="WO20", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO20").to_be_considered or 0)
        attributes['production_planning'] = (Ke5z_updated.objects.filter(functional_area="WO21", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO21").to_be_considered or 0)
        attributes['facility_costs'] = (Ke5z_updated.objects.filter(functional_area="WO22", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO22").to_be_considered or 0)
        attributes['maintenance_dept'] = (Ke5z_updated.objects.filter(functional_area="WO23", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO23").to_be_considered or 0)
        attributes['production_eng'] = (Ke5z_updated.objects.filter(functional_area="WO24", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO24").to_be_considered or 0)
        attributes['production_management'] = (Ke5z_updated.objects.filter(functional_area="WO25", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO25").to_be_considered or 0)
        attributes['quality_production'] = (Ke5z_updated.objects.filter(functional_area="WO26", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO26").to_be_considered or 0)
        attributes['quality_general'] = (Ke5z_updated.objects.filter(functional_area="WO27", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO27").to_be_considered or 0)
        attributes['purchasing_indirect_material'] = (Ke5z_updated.objects.filter(functional_area="WO28", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO28").to_be_considered or 0)
        attributes['warranty_plant'] = (Ke5z_updated.objects.filter(functional_area="WO29", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO29").to_be_considered or 0)
        attributes['target_poc_overhead'] = (Ke5z_updated.objects.filter(functional_area="WO30", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO30").to_be_considered or 0)
        attributes['target_gen_costs'] = (Ke5z_updated.objects.filter(functional_area="WO31", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="WO31").to_be_considered or 0)
        attributes['manufacturing_overhead'] = attributes['target_gen_costs'] + attributes['target_poc_overhead'] + attributes['warranty_plant'] + attributes['purchasing_indirect_material'] + attributes['quality_general'] + attributes['quality_production'] + attributes['production_management'] + attributes['production_eng'] + attributes['maintenance_dept'] + attributes['facility_costs'] + attributes['production_planning'] + attributes['energy_utilities'] + attributes['production_supply'] + attributes['welding_direct_production_overhead']  + attributes['remanufacturing_overhead'] + attributes['other_direct_production_cost_centers_overhead'] + attributes['surface_treatment_overhead'] + attributes['pre_machining_overhead'] + attributes['pre_assembly_overhead'] + attributes['machining_overhead'] + attributes['assembly_overhead']
        attributes['manufacturing_overhead_in_of_gross_sales'] = (attributes['manufacturing_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['manufacturing_overhead_in_of_net_sales'] = (attributes['manufacturing_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['hk_1'] = attributes['manufacturing_overhead'] + attributes['direct_labour'] + attributes['material_overhead'] + attributes['material_direct']
        attributes['gross_profit_operating_performance'] = attributes['hk_1'] + attributes['total_operating_performance']
        attributes['gross_profit_in_of_gross_sales'] = (attributes['gross_profit_operating_performance'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['gross_profit_after_other_rev_in_of_net_sales'] = (attributes['gross_profit_operating_performance'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['general_management'] = (Ke5z_updated.objects.filter(functional_area="AD11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD11").to_be_considered or 0)
        attributes['plant_admin'] = (Ke5z_updated.objects.filter(functional_area="AD12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD12").to_be_considered or 0)
        attributes['central_functions'] = (Ke5z_updated.objects.filter(functional_area="AD13", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD13").to_be_considered or 0)
        attributes['central_function_indirect_purchasing'] = (Ke5z_updated.objects.filter(functional_area="AD14", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD14").to_be_considered or 0)
        attributes['information_technology'] = (Ke5z_updated.objects.filter(functional_area="AD15", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD15").to_be_considered or 0)
        attributes['admin_facility_costs_energy'] = (Ke5z_updated.objects.filter(functional_area="AD16", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD16").to_be_considered or 0)
        attributes['special_projects'] = (Ke5z_updated.objects.filter(functional_area="AD17", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD17").to_be_considered or 0)
        attributes['target_poc'] = (Ke5z_updated.objects.filter(functional_area="AD18", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD18").to_be_considered or 0)
        attributes['target_gen_costs'] = (Ke5z_updated.objects.filter(functional_area="AD19", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD19").to_be_considered or 0)
        attributes['central_function_direct_purchasing'] = (Ke5z_updated.objects.filter(functional_area="AD21", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD21").to_be_considered or 0)
        attributes['central_function_industrial_engineering'] = (Ke5z_updated.objects.filter(functional_area="AD22", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD22").to_be_considered or 0)
        attributes['central_function_logistics'] = (Ke5z_updated.objects.filter(functional_area="AD23", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD23").to_be_considered or 0)
        attributes['hr'] = (Ke5z_updated.objects.filter(functional_area="AD24", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD24").to_be_considered or 0)
        attributes['plant_hr'] = (Ke5z_updated.objects.filter(functional_area="AD25", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD25").to_be_considered or 0)
        attributes['finance_controlling'] = (Ke5z_updated.objects.filter(functional_area="AD26", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD26").to_be_considered or 0)
        attributes['plant_finance_controlling'] = (Ke5z_updated.objects.filter(functional_area="AD27", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD27").to_be_considered or 0)
        attributes['central_quality_management'] = (Ke5z_updated.objects.filter(functional_area="AD28", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD28").to_be_considered or 0)
        attributes['apprenticeship_trainee_programs'] = (Ke5z_updated.objects.filter(functional_area="AD29", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD29").to_be_considered or 0)
        attributes['other_central_support_functions'] = (Ke5z_updated.objects.filter(functional_area="AD30", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD30").to_be_considered or 0)
        attributes['other_plant_support_functions'] = (Ke5z_updated.objects.filter(functional_area="AD31", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="AD31").to_be_considered or 0)
        attributes['admin'] = attributes['general_management'] + attributes['plant_admin'] + attributes['central_functions'] + attributes['central_function_indirect_purchasing'] + attributes['information_technology'] + attributes['admin_facility_costs_energy'] + attributes['special_projects'] + attributes['target_poc'] + attributes['target_gen_costs'] + attributes['central_function_direct_purchasing'] + attributes['central_function_industrial_engineering'] + attributes['central_function_logistics'] + attributes['hr'] + attributes['plant_hr'] + attributes['finance_controlling'] + attributes['plant_finance_controlling'] + attributes['central_quality_management'] + attributes['apprenticeship_trainee_programs'] + attributes['other_central_support_functions'] + attributes['other_plant_support_functions']
        attributes['admin_in_of_net_sales'] = (attributes['admin'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['customer_service_plant'] = (Ke5z_updated.objects.filter(functional_area="SM11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM11").to_be_considered or 0)
        attributes['central_customer_service'] = (Ke5z_updated.objects.filter(functional_area="SM12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM12").to_be_considered or 0)
        attributes['marketing'] = (Ke5z_updated.objects.filter(functional_area="SM13", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM13").to_be_considered or 0)
        attributes['sales_force'] = (Ke5z_updated.objects.filter(functional_area="SM14", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM14").to_be_considered or 0)
        attributes['outbound_logistic_plant'] = (Ke5z_updated.objects.filter(functional_area="SM15", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM15").to_be_considered or 0)
        attributes['sales_logistic'] = (Ke5z_updated.objects.filter(functional_area="SM16", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM16").to_be_considered or 0)
        attributes['freight_out'] = (Ke5z_updated.objects.filter(functional_area="SM17", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM17").to_be_considered or 0)
        attributes['target_poc'] = (Ke5z_updated.objects.filter(functional_area="SM18", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM18").to_be_considered or 0)
        attributes['target_gen_costs'] = (Ke5z_updated.objects.filter(functional_area="SM19", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM19").to_be_considered or 0)
        attributes['sales_facility_costs_energy'] = (Ke5z_updated.objects.filter(functional_area="SM26", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM26").to_be_considered or 0)
        attributes['other_sales_costs'] = (Ke5z_updated.objects.filter(functional_area="SM27", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM27").to_be_considered or 0)
        attributes['sales_income'] = (Ke5z_updated.objects.filter(functional_area="SM28", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM28").to_be_considered or 0)
        attributes['sales_managment'] = (Ke5z_updated.objects.filter(functional_area="SM29", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="SM29").to_be_considered or 0)
        attributes['sales_marketing'] = attributes['sales_managment'] + attributes['sales_income'] + attributes['other_sales_costs'] + attributes['sales_facility_costs_energy'] + attributes['target_gen_costs'] + attributes['target_poc'] + attributes['freight_out'] + attributes['sales_logistic'] + attributes['outbound_logistic_plant'] + attributes['sales_force'] + attributes['marketing'] + attributes['central_customer_service'] + attributes['customer_service_plant']
        attributes['sales_marketing_in_of_net_sales'] = (attributes['sales_marketing'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['general_rd_engineering_management_admin'] = (Ke5z_updated.objects.filter(functional_area="RD10", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="RD10").to_be_considered or 0)
        attributes['advanced_eng_innovation_mgt'] = (Ke5z_updated.objects.filter(functional_area="RD11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="RD11").to_be_considered or 0)
        attributes['engineering'] = (Ke5z_updated.objects.filter(functional_area="RD12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="RD12").to_be_considered or 0)
        attributes['platform_engineering_service'] = (Ke5z_updated.objects.filter(functional_area="RD13", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="RD13").to_be_considered or 0)
        attributes['rd_facility_costs_energy'] = (Ke5z_updated.objects.filter(functional_area="RD14", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="RD14").to_be_considered or 0)
        attributes['rd_tooling'] = (Ke5z_updated.objects.filter(functional_area="RD15", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="RD15").to_be_considered or 0)
        attributes['rd_system_engineering'] = (Ke5z_updated.objects.filter(functional_area="RD16", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="RD16").to_be_considered or 0)
        attributes['rd_target_gc'] = (Ke5z_updated.objects.filter(functional_area="RD17", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="RD17").to_be_considered or 0)
        attributes['product_management'] = (Ke5z_updated.objects.filter(functional_area="RD24", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="RD24").to_be_considered or 0)
        attributes['rd'] = attributes['product_management'] + attributes['rd_target_gc'] + attributes['rd_system_engineering'] + attributes['rd_tooling'] + attributes['rd_facility_costs_energy'] + attributes['platform_engineering_service'] + attributes['engineering'] + attributes['advanced_eng_innovation_mgt'] + attributes['general_rd_engineering_management_admin']
        attributes['rd_in_of_net_sales'] = (attributes['rd'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['primary_result'] = attributes['rd'] + attributes['sales_marketing'] + attributes['admin'] + attributes['gross_profit_operating_performance']
        attributes['primary_result_in_of_net_sales'] = (attributes['primary_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['intercompany_charges'] = (Ke5z_updated.objects.filter(functional_area="IC11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="IC11").to_be_considered or 0)
        attributes['ic_hq'] = attributes['intercompany_charges']
        attributes['ic_charges_in_of_net_sales'] = (attributes['ic_hq'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['other_plant'] = (Ke5z_updated.objects.filter(functional_area="OT01", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="OT01").to_be_considered or 0)
        attributes['other_general_costs'] = (Ke5z_updated.objects.filter(functional_area="OT02", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="OT02").to_be_considered or 0)
        attributes['customer_quality_campaigns'] = (Ke5z_updated.objects.filter(functional_area="OT03", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="OT03").to_be_considered or 0)
        attributes['other'] = attributes['customer_quality_campaigns'] + attributes['other_general_costs'] + attributes['other_plant']
        attributes['other_in_of_net_sales']  = (attributes['other'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['ebit'] = attributes['primary_result'] + attributes['other']
        attributes['ebit_in_of_net_sales'] = (attributes['ebit'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['interest_result'] = (Ke5z_updated.objects.filter(functional_area="FR11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="FR11").to_be_considered or 0)
        attributes['income_from_investments'] = (Ke5z_updated.objects.filter(functional_area="FR12", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="FR12").to_be_considered or 0)
        attributes['financial_result'] = attributes['interest_result'] + attributes['income_from_investments']
        attributes['financial_result_in_of_net_sales'] = (attributes['financial_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['pb_t'] = attributes['ebit'] + attributes['financial_result']
        attributes['ros_in'] = (attributes['pb_t'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['extraordinary_result'] = (Ke5z_updated.objects.filter(functional_area="EO11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="EO11").to_be_considered or 0)
        attributes['extraordinary_result_2'] = attributes['extraordinary_result']
        attributes['profit_loss_transfer'] = (Ke5z_updated.objects.filter(functional_area="PL11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="PL11").to_be_considered or 0)
        attributes['profit_loss_transfer_2'] = attributes['profit_loss_transfer']
        attributes['income_tax'] = (Ke5z_updated.objects.filter(functional_area="TX11", record_type=0, posting_period=month, fiscal_year=year).aggregate(sum=Sum('in_profit_center_local_currency'))['sum'] or 0) + (Closing_Corrections.objects.safe_get(month=month, year=year, functional_area="TX11").to_be_considered or 0)
        attributes['income_tax_2'] = attributes['income_tax']
        attributes['company_result'] = attributes['pb_t'] + attributes['extraordinary_result_2'] + attributes['profit_loss_transfer_2'] + attributes['income_tax_2']
        attributes['own_production_operating_performance'] = attributes['gross_sales_own_production'] + attributes['inventory_change']

        Actual_Costbook.objects.update_or_create(month=month, year=year, defaults=attributes)

    return HttpResponse("OK")


def Budget_Flexed_Costbook_recalc(request=None, month=None, year=None):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
    else:
        if not year:
            year = 2021

    if not month:
        for i in range(1,13):
            attributes = {}
            attributes['gross_sales_merchandized_3p'] = MOP.objects.filter(year=year, functional_area="SA01").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['gross_sales_merchandized_ic'] = MOP.objects.filter(year=year, functional_area="SA02").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['gross_sales_merchandized'] = attributes['gross_sales_merchandized_3p'] + attributes['gross_sales_merchandized_ic']
            attributes['gross_sales_own_production_3p'] = MOP.objects.filter(year=year, functional_area="SA03").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['gross_sales_own_production_ic'] = MOP.objects.filter(year=year, functional_area="SA04").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['gross_sales_own_production'] = attributes['gross_sales_own_production_3p'] + attributes['gross_sales_own_production_ic']
            attributes['gross_sales'] = attributes['gross_sales_merchandized'] + attributes['gross_sales_own_production']
            attributes['customer_discounts'] = MOP.objects.filter(year=year, functional_area="OR11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['pricing_differences'] = MOP.objects.filter(year=year, functional_area="OR12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['royalties_licences_3p'] = MOP.objects.filter(year=year, functional_area="OR13").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['core_revenues'] = MOP.objects.filter(year=year, functional_area="OR14").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['income_from_scrap'] = MOP.objects.filter(year=year, functional_area="OR15").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['other_revenues'] = attributes['customer_discounts'] + attributes['pricing_differences'] + attributes['royalties_licences_3p'] + attributes['core_revenues'] + attributes['income_from_scrap']
            attributes['other_revenues_in_of_gross_sales'] = (attributes['other_revenues'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['net_sales'] = attributes['other_revenues'] + attributes['gross_sales']
            attributes['increase_decrease_of_finished_goods_wip_hk_1'] = MOP.objects.filter(year=year, functional_area="IN11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1'] = MOP.objects.filter(year=year, functional_area="IN12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['inventory_change'] = attributes['increase_decrease_of_finished_goods_wip_hk_1'] + attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1']
            attributes['self_constructed_assets'] = MOP.objects.filter(year=year, functional_area="OW11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['own_work_capitalized'] = attributes['self_constructed_assets']
            attributes['total_operating_performance'] = attributes['own_work_capitalized'] + attributes['inventory_change'] + attributes['net_sales']
            attributes['direct_production_material'] = MOP.objects.filter(year=year, functional_area="MD11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['merchandise_parts'] = MOP.objects.filter(year=year, functional_area="MD12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['sub_contracting'] = MOP.objects.filter(year=year, functional_area="MD13").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['excess_obsolete_stock'] = MOP.objects.filter(year=year, functional_area="MD14").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['scrap'] = MOP.objects.filter(year=year, functional_area="MD15").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['increase_decrease_of_finished_goods_wip'] = MOP.objects.filter(year=year, functional_area="MD16").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target'] = MOP.objects.filter(year=year, functional_area="MD17").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['inventory_shrink_and_revaluations'] = MOP.objects.filter(year=year, functional_area="MD18").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['material_direct'] = attributes['direct_production_material'] + attributes['merchandise_parts'] + attributes['sub_contracting'] + attributes['excess_obsolete_stock'] + attributes['scrap'] + attributes['increase_decrease_of_finished_goods_wip'] + attributes['target'] + attributes['inventory_shrink_and_revaluations']
            attributes['material_direct_in_of_gross_sales'] = (attributes['material_direct'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['material_direct_in_of_operating_performance'] = (attributes['material_direct'] / attributes['total_operating_performance']) if attributes['total_operating_performance'] else 0
            attributes['purchase_mat_di'] = MOP.objects.filter(year=year, functional_area="MO11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['tooling_supplier'] = MOP.objects.filter(year=year, functional_area="MO12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['procurement'] = MOP.objects.filter(year=year, functional_area="MO13").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['freight_in'] = MOP.objects.filter(year=year, functional_area="MO14").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['inbound_logistic'] = MOP.objects.filter(year=year, functional_area="MO15").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['quality_supplier'] = MOP.objects.filter(year=year, functional_area="MO16").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="MO17").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="MO18").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['material_overhead'] = attributes['target_gen_costs'] + attributes['target_poc'] + attributes['quality_supplier'] + attributes['inbound_logistic'] + attributes['freight_in'] + attributes['procurement'] + attributes['tooling_supplier'] + attributes['purchase_mat_di']
            attributes['material_overhead_in_of_gross_sales'] = (attributes['material_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['material_overhead_in_of_net_sales'] = (attributes['material_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['assembly_direct'] = MOP.objects.filter(year=year, functional_area="WD11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['machining_direct'] = MOP.objects.filter(year=year, functional_area="WD12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['pre_assembly_direct'] = MOP.objects.filter(year=year, functional_area="WD13").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['pre_machining_direct'] = MOP.objects.filter(year=year, functional_area="WD14").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['surface_treatment_direct'] = MOP.objects.filter(year=year, functional_area="WD15").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['other_direct_production_cost_centers_direct'] = MOP.objects.filter(year=year, functional_area="WD16").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['remanufacturing_direct'] = MOP.objects.filter(year=year, functional_area="WD17").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['welding_direct_production_direct'] = MOP.objects.filter(year=year, functional_area="WD18").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target_poc_direct'] = MOP.objects.filter(year=year, functional_area="WD19").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['direct_labour'] = attributes['target_poc_direct'] + attributes['welding_direct_production_direct'] + attributes['remanufacturing_direct'] + attributes['other_direct_production_cost_centers_direct'] + attributes['surface_treatment_direct'] + attributes['pre_machining_direct'] + attributes['pre_assembly_direct'] + attributes['machining_direct'] + attributes['assembly_direct']
            attributes['direct_labour_in_of_gross_sales'] = (attributes['direct_labour'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['direct_labour_in_of_net_sales'] = (attributes['direct_labour'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['direct_labour_in_of_sales_own_production'] = (attributes['direct_labour'] / attributes['gross_sales_own_production']) if attributes['gross_sales_own_production'] else 0
            attributes['assembly_overhead'] = MOP.objects.filter(year=year, functional_area="WO11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['machining_overhead'] = MOP.objects.filter(year=year, functional_area="WO12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['pre_assembly_overhead'] = MOP.objects.filter(year=year, functional_area="WO13").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['pre_machining_overhead'] = MOP.objects.filter(year=year, functional_area="WO14").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['surface_treatment_overhead'] = MOP.objects.filter(year=year, functional_area="WO15").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['other_direct_production_cost_centers_overhead'] = MOP.objects.filter(year=year, functional_area="WO16").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['remanufacturing_overhead'] = MOP.objects.filter(year=year, functional_area="WO17").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['welding_direct_production_overhead'] = MOP.objects.filter(year=year, functional_area="WO18").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['production_supply'] = MOP.objects.filter(year=year, functional_area="WO19").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['energy_utilities'] = MOP.objects.filter(year=year, functional_area="WO20").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['production_planning'] = MOP.objects.filter(year=year, functional_area="WO21").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['facility_costs'] = MOP.objects.filter(year=year, functional_area="WO22").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['maintenance_dept'] = MOP.objects.filter(year=year, functional_area="WO23").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['production_eng'] =MOP.objects.filter(year=year, functional_area="WO24").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['production_management'] = MOP.objects.filter(year=year, functional_area="WO25").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['quality_production'] = MOP.objects.filter(year=year, functional_area="WO26").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['quality_general'] = MOP.objects.filter(year=year, functional_area="WO27").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['purchasing_indirect_material'] = MOP.objects.filter(year=year, functional_area="WO28").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['warranty_plant'] = MOP.objects.filter(year=year, functional_area="WO29").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target_poc_overhead'] = MOP.objects.filter(year=year, functional_area="WO30").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="WO31").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['manufacturing_overhead'] = attributes['target_gen_costs'] + attributes['target_poc_overhead'] + attributes['warranty_plant'] + attributes['purchasing_indirect_material'] + attributes['quality_general'] + attributes['quality_production'] + attributes['production_management'] + attributes['production_eng'] + attributes['maintenance_dept'] + attributes['facility_costs'] + attributes['production_planning'] + attributes['energy_utilities'] + attributes['production_supply'] + attributes['welding_direct_production_overhead']  + attributes['remanufacturing_overhead'] + attributes['other_direct_production_cost_centers_overhead'] + attributes['surface_treatment_overhead'] + attributes['pre_machining_overhead'] + attributes['pre_assembly_overhead'] + attributes['machining_overhead'] + attributes['assembly_overhead']
            attributes['manufacturing_overhead_in_of_gross_sales'] = (attributes['manufacturing_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['manufacturing_overhead_in_of_net_sales'] = (attributes['manufacturing_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['hk_1'] = attributes['manufacturing_overhead'] + attributes['direct_labour'] + attributes['material_overhead'] + attributes['material_direct']
            attributes['gross_profit_operating_performance'] = attributes['hk_1'] + attributes['total_operating_performance']
            attributes['gross_profit_in_of_gross_sales'] = (attributes['gross_profit_operating_performance'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['gross_profit_after_other_rev_in_of_net_sales'] = (attributes['gross_profit_operating_performance'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['general_management'] = MOP.objects.filter(year=year, functional_area="AD11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['plant_admin'] = MOP.objects.filter(year=year, functional_area="AD12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['central_functions'] = MOP.objects.filter(year=year, functional_area="AD13").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['central_function_indirect_purchasing'] = MOP.objects.filter(year=year, functional_area="AD14").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['information_technology'] = MOP.objects.filter(year=year, functional_area="AD15").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['admin_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="AD16").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['special_projects'] = MOP.objects.filter(year=year, functional_area="AD17").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="AD18").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="AD19").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['central_function_direct_purchasing'] = MOP.objects.filter(year=year, functional_area="AD21").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['central_function_industrial_engineering'] = MOP.objects.filter(year=year, functional_area="AD22").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['central_function_logistics'] = MOP.objects.filter(year=year, functional_area="AD23").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['hr'] = MOP.objects.filter(year=year, functional_area="AD24").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['plant_hr'] = MOP.objects.filter(year=year, functional_area="AD25").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['finance_controlling'] = MOP.objects.filter(year=year, functional_area="AD26").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['plant_finance_controlling'] = MOP.objects.filter(year=year, functional_area="AD27").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['central_quality_management'] = MOP.objects.filter(year=year, functional_area="AD28").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['apprenticeship_trainee_programs'] = MOP.objects.filter(year=year, functional_area="AD29").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['other_central_support_functions'] = MOP.objects.filter(year=year, functional_area="AD30").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['other_plant_support_functions'] = MOP.objects.filter(year=year, functional_area="AD31").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['admin'] = attributes['general_management'] + attributes['plant_admin'] + attributes['central_functions'] + attributes['central_function_indirect_purchasing'] + attributes['information_technology'] + attributes['admin_facility_costs_energy'] + attributes['special_projects'] + attributes['target_poc'] + attributes['target_gen_costs'] + attributes['central_function_direct_purchasing'] + attributes['central_function_industrial_engineering'] + attributes['central_function_logistics'] + attributes['hr'] + attributes['plant_hr'] + attributes['finance_controlling'] + attributes['plant_finance_controlling'] + attributes['central_quality_management'] + attributes['apprenticeship_trainee_programs'] + attributes['other_central_support_functions'] + attributes['other_plant_support_functions']
            attributes['admin_in_of_net_sales'] = (attributes['admin'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['customer_service_plant'] = MOP.objects.filter(year=year, functional_area="SM11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['central_customer_service'] = MOP.objects.filter(year=year, functional_area="SM12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['marketing'] = MOP.objects.filter(year=year, functional_area="SM13").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['sales_force'] = MOP.objects.filter(year=year, functional_area="SM14").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['outbound_logistic_plant'] = MOP.objects.filter(year=year, functional_area="SM15").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['sales_logistic'] = MOP.objects.filter(year=year, functional_area="SM16").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['freight_out'] = MOP.objects.filter(year=year, functional_area="SM17").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="SM18").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="SM19").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['sales_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="SM26").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['other_sales_costs'] = MOP.objects.filter(year=year, functional_area="SM27").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['sales_income'] = MOP.objects.filter(year=year, functional_area="SM28").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['sales_managment'] = MOP.objects.filter(year=year, functional_area="SM29").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['sales_marketing'] = attributes['sales_managment'] + attributes['sales_income'] + attributes['other_sales_costs'] + attributes['sales_facility_costs_energy'] + attributes['target_gen_costs'] + attributes['target_poc'] + attributes['freight_out'] + attributes['sales_logistic'] + attributes['outbound_logistic_plant'] + attributes['sales_force'] + attributes['marketing'] + attributes['central_customer_service'] + attributes['customer_service_plant']
            attributes['sales_marketing_in_of_net_sales'] = (attributes['sales_marketing'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['general_rd_engineering_management_admin'] = MOP.objects.filter(year=year, functional_area="RD10").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['advanced_eng_innovation_mgt'] = MOP.objects.filter(year=year, functional_area="RD11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['engineering'] = MOP.objects.filter(year=year, functional_area="RD12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['platform_engineering_service'] = MOP.objects.filter(year=year, functional_area="RD13").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['rd_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="RD14").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['rd_tooling'] = MOP.objects.filter(year=year, functional_area="RD15").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['rd_system_engineering'] = MOP.objects.filter(year=year, functional_area="RD16").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['rd_target_gc'] = MOP.objects.filter(year=year, functional_area="RD17").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['product_management'] = MOP.objects.filter(year=year, functional_area="RD24").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['rd'] = attributes['product_management'] + attributes['rd_target_gc'] + attributes['rd_system_engineering'] + attributes['rd_tooling'] + attributes['rd_facility_costs_energy'] + attributes['platform_engineering_service'] + attributes['engineering'] + attributes['advanced_eng_innovation_mgt'] + attributes['general_rd_engineering_management_admin']
            attributes['rd_in_of_net_sales'] = (attributes['rd'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['primary_result'] = attributes['rd'] + attributes['sales_marketing'] + attributes['admin'] + attributes['gross_profit_operating_performance']
            attributes['primary_result_in_of_net_sales'] = (attributes['primary_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['intercompany_charges'] = MOP.objects.filter(year=year, functional_area="IC11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['ic_hq'] = attributes['intercompany_charges']
            attributes['ic_charges_in_of_net_sales'] = (attributes['ic_hq'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['other_plant'] = MOP.objects.filter(year=year, functional_area="OT01").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
            attributes['other_general_costs'] = MOP.objects.filter(year=year, functional_area="OT02").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
            attributes['customer_quality_campaigns'] = MOP.objects.filter(year=year, functional_area="OT03").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
            attributes['other'] = attributes['customer_quality_campaigns'] + attributes['other_general_costs'] + attributes['other_plant']
            attributes['other_in_of_net_sales']  = (attributes['other'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['ebit'] = attributes['primary_result'] + attributes['other']
            attributes['ebit_in_of_net_sales'] = (attributes['ebit'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['interest_result'] = MOP.objects.filter(year=year, functional_area="FR11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['income_from_investments'] = MOP.objects.filter(year=year, functional_area="FR12").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['financial_result'] = attributes['interest_result'] + attributes['income_from_investments']
            attributes['financial_result_in_of_net_sales'] = (attributes['financial_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['pb_t'] = attributes['ebit'] + attributes['financial_result']
            attributes['ros_in'] = (attributes['pb_t'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['extraordinary_result'] = MOP.objects.filter(year=year, functional_area="EO11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['extraordinary_result_2'] = attributes['extraordinary_result']
            attributes['profit_loss_transfer'] = MOP.objects.filter(year=year, functional_area="PL11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['profit_loss_transfer_2'] = attributes['profit_loss_transfer']
            attributes['income_tax'] = MOP.objects.filter(year=year, functional_area="TX11").aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            attributes['income_tax_2'] = attributes['income_tax']
            attributes['company_result'] = attributes['pb_t'] + attributes['extraordinary_result_2'] + attributes['profit_loss_transfer_2'] + attributes['income_tax_2']
            attributes['own_production_operating_performance'] = attributes['gross_sales_own_production'] + attributes['inventory_change']

            Budget_Flexed_Costbook.objects.update_or_create(month=i, year=year, defaults=attributes)
    else:
        attributes = {}
        attributes['gross_sales_merchandized_3p'] = MOP.objects.filter(year=year, functional_area="SA01").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['gross_sales_merchandized_ic'] = MOP.objects.filter(year=year, functional_area="SA02").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['gross_sales_merchandized'] = attributes['gross_sales_merchandized_3p'] + attributes['gross_sales_merchandized_ic']
        attributes['gross_sales_own_production_3p'] = MOP.objects.filter(year=year, functional_area="SA03").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['gross_sales_own_production_ic'] = MOP.objects.filter(year=year, functional_area="SA04").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['gross_sales_own_production'] = attributes['gross_sales_own_production_3p'] + attributes['gross_sales_own_production_ic']
        attributes['gross_sales'] = attributes['gross_sales_merchandized'] + attributes['gross_sales_own_production']
        attributes['customer_discounts'] = MOP.objects.filter(year=year, functional_area="OR11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['pricing_differences'] = MOP.objects.filter(year=year, functional_area="OR12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['royalties_licences_3p'] = MOP.objects.filter(year=year, functional_area="OR13").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['core_revenues'] = MOP.objects.filter(year=year, functional_area="OR14").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['income_from_scrap'] = MOP.objects.filter(year=year, functional_area="OR15").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['other_revenues'] = attributes['customer_discounts'] + attributes['pricing_differences'] + attributes['royalties_licences_3p'] + attributes['core_revenues'] + attributes['income_from_scrap']
        attributes['other_revenues_in_of_gross_sales'] = (attributes['other_revenues'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['net_sales'] = attributes['other_revenues'] + attributes['gross_sales']
        attributes['increase_decrease_of_finished_goods_wip_hk_1'] = MOP.objects.filter(year=year, functional_area="IN11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1'] = MOP.objects.filter(year=year, functional_area="IN12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['inventory_change'] = attributes['increase_decrease_of_finished_goods_wip_hk_1'] + attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1']
        attributes['self_constructed_assets'] = MOP.objects.filter(year=year, functional_area="OW11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['own_work_capitalized'] = attributes['self_constructed_assets']
        attributes['total_operating_performance'] = attributes['own_work_capitalized'] + attributes['inventory_change'] + attributes['net_sales']
        attributes['direct_production_material'] = MOP.objects.filter(year=year, functional_area="MD11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['merchandise_parts'] = MOP.objects.filter(year=year, functional_area="MD12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['sub_contracting'] = MOP.objects.filter(year=year, functional_area="MD13").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['excess_obsolete_stock'] = MOP.objects.filter(year=year, functional_area="MD14").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['scrap'] = MOP.objects.filter(year=year, functional_area="MD15").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['increase_decrease_of_finished_goods_wip'] = MOP.objects.filter(year=year, functional_area="MD16").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target'] = MOP.objects.filter(year=year, functional_area="MD17").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['inventory_shrink_and_revaluations'] = MOP.objects.filter(year=year, functional_area="MD18").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['material_direct'] = attributes['direct_production_material'] + attributes['merchandise_parts'] + attributes['sub_contracting'] + attributes['excess_obsolete_stock'] + attributes['scrap'] + attributes['increase_decrease_of_finished_goods_wip'] + attributes['target'] + attributes['inventory_shrink_and_revaluations']
        attributes['material_direct_in_of_gross_sales'] = (attributes['material_direct'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['material_direct_in_of_operating_performance'] = (attributes['material_direct'] / attributes['total_operating_performance']) if attributes['total_operating_performance'] else 0
        attributes['purchase_mat_di'] = MOP.objects.filter(year=year, functional_area="MO11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['tooling_supplier'] = MOP.objects.filter(year=year, functional_area="MO12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['procurement'] = MOP.objects.filter(year=year, functional_area="MO13").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['freight_in'] = MOP.objects.filter(year=year, functional_area="MO14").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['inbound_logistic'] = MOP.objects.filter(year=year, functional_area="MO15").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['quality_supplier'] = MOP.objects.filter(year=year, functional_area="MO16").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="MO17").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="MO18").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['material_overhead'] = attributes['target_gen_costs'] + attributes['target_poc'] + attributes['quality_supplier'] + attributes['inbound_logistic'] + attributes['freight_in'] + attributes['procurement'] + attributes['tooling_supplier'] + attributes['purchase_mat_di']
        attributes['material_overhead_in_of_gross_sales'] = (attributes['material_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['material_overhead_in_of_net_sales'] = (attributes['material_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['assembly_direct'] = MOP.objects.filter(year=year, functional_area="WD11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['machining_direct'] = MOP.objects.filter(year=year, functional_area="WD12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['pre_assembly_direct'] = MOP.objects.filter(year=year, functional_area="WD13").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['pre_machining_direct'] = MOP.objects.filter(year=year, functional_area="WD14").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['surface_treatment_direct'] = MOP.objects.filter(year=year, functional_area="WD15").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['other_direct_production_cost_centers_direct'] = MOP.objects.filter(year=year, functional_area="WD16").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['remanufacturing_direct'] = MOP.objects.filter(year=year, functional_area="WD17").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['welding_direct_production_direct'] = MOP.objects.filter(year=year, functional_area="WD18").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target_poc_direct'] = MOP.objects.filter(year=year, functional_area="WD19").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['direct_labour'] = attributes['target_poc_direct'] + attributes['welding_direct_production_direct'] + attributes['remanufacturing_direct'] + attributes['other_direct_production_cost_centers_direct'] + attributes['surface_treatment_direct'] + attributes['pre_machining_direct'] + attributes['pre_assembly_direct'] + attributes['machining_direct'] + attributes['assembly_direct']
        attributes['direct_labour_in_of_gross_sales'] = (attributes['direct_labour'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['direct_labour_in_of_net_sales'] = (attributes['direct_labour'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['direct_labour_in_of_sales_own_production'] = (attributes['direct_labour'] / attributes['gross_sales_own_production']) if attributes['gross_sales_own_production'] else 0
        attributes['assembly_overhead'] = MOP.objects.filter(year=year, functional_area="WO11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['machining_overhead'] = MOP.objects.filter(year=year, functional_area="WO12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['pre_assembly_overhead'] = MOP.objects.filter(year=year, functional_area="WO13").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['pre_machining_overhead'] = MOP.objects.filter(year=year, functional_area="WO14").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['surface_treatment_overhead'] = MOP.objects.filter(year=year, functional_area="WO15").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['other_direct_production_cost_centers_overhead'] = MOP.objects.filter(year=year, functional_area="WO16").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['remanufacturing_overhead'] = MOP.objects.filter(year=year, functional_area="WO17").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['welding_direct_production_overhead'] = MOP.objects.filter(year=year, functional_area="WO18").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['production_supply'] = MOP.objects.filter(year=year, functional_area="WO19").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['energy_utilities'] = MOP.objects.filter(year=year, functional_area="WO20").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['production_planning'] = MOP.objects.filter(year=year, functional_area="WO21").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['facility_costs'] = MOP.objects.filter(year=year, functional_area="WO22").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['maintenance_dept'] = MOP.objects.filter(year=year, functional_area="WO23").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['production_eng'] =MOP.objects.filter(year=year, functional_area="WO24").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['production_management'] = MOP.objects.filter(year=year, functional_area="WO25").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['quality_production'] = MOP.objects.filter(year=year, functional_area="WO26").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['quality_general'] = MOP.objects.filter(year=year, functional_area="WO27").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['purchasing_indirect_material'] = MOP.objects.filter(year=year, functional_area="WO28").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['warranty_plant'] = MOP.objects.filter(year=year, functional_area="WO29").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target_poc_overhead'] = MOP.objects.filter(year=year, functional_area="WO30").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="WO31").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['manufacturing_overhead'] = attributes['target_gen_costs'] + attributes['target_poc_overhead'] + attributes['warranty_plant'] + attributes['purchasing_indirect_material'] + attributes['quality_general'] + attributes['quality_production'] + attributes['production_management'] + attributes['production_eng'] + attributes['maintenance_dept'] + attributes['facility_costs'] + attributes['production_planning'] + attributes['energy_utilities'] + attributes['production_supply'] + attributes['welding_direct_production_overhead']  + attributes['remanufacturing_overhead'] + attributes['other_direct_production_cost_centers_overhead'] + attributes['surface_treatment_overhead'] + attributes['pre_machining_overhead'] + attributes['pre_assembly_overhead'] + attributes['machining_overhead'] + attributes['assembly_overhead']
        attributes['manufacturing_overhead_in_of_gross_sales'] = (attributes['manufacturing_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['manufacturing_overhead_in_of_net_sales'] = (attributes['manufacturing_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['hk_1'] = attributes['manufacturing_overhead'] + attributes['direct_labour'] + attributes['material_overhead'] + attributes['material_direct']
        attributes['gross_profit_operating_performance'] = attributes['hk_1'] + attributes['total_operating_performance']
        attributes['gross_profit_in_of_gross_sales'] = (attributes['gross_profit_operating_performance'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['gross_profit_after_other_rev_in_of_net_sales'] = (attributes['gross_profit_operating_performance'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['general_management'] = MOP.objects.filter(year=year, functional_area="AD11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['plant_admin'] = MOP.objects.filter(year=year, functional_area="AD12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['central_functions'] = MOP.objects.filter(year=year, functional_area="AD13").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['central_function_indirect_purchasing'] = MOP.objects.filter(year=year, functional_area="AD14").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['information_technology'] = MOP.objects.filter(year=year, functional_area="AD15").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['admin_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="AD16").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['special_projects'] = MOP.objects.filter(year=year, functional_area="AD17").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="AD18").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="AD19").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['central_function_direct_purchasing'] = MOP.objects.filter(year=year, functional_area="AD21").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['central_function_industrial_engineering'] = MOP.objects.filter(year=year, functional_area="AD22").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['central_function_logistics'] = MOP.objects.filter(year=year, functional_area="AD23").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['hr'] = MOP.objects.filter(year=year, functional_area="AD24").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['plant_hr'] = MOP.objects.filter(year=year, functional_area="AD25").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['finance_controlling'] = MOP.objects.filter(year=year, functional_area="AD26").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['plant_finance_controlling'] = MOP.objects.filter(year=year, functional_area="AD27").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['central_quality_management'] = MOP.objects.filter(year=year, functional_area="AD28").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['apprenticeship_trainee_programs'] = MOP.objects.filter(year=year, functional_area="AD29").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['other_central_support_functions'] = MOP.objects.filter(year=year, functional_area="AD30").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['other_plant_support_functions'] = MOP.objects.filter(year=year, functional_area="AD31").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['admin'] = attributes['general_management'] + attributes['plant_admin'] + attributes['central_functions'] + attributes['central_function_indirect_purchasing'] + attributes['information_technology'] + attributes['admin_facility_costs_energy'] + attributes['special_projects'] + attributes['target_poc'] + attributes['target_gen_costs'] + attributes['central_function_direct_purchasing'] + attributes['central_function_industrial_engineering'] + attributes['central_function_logistics'] + attributes['hr'] + attributes['plant_hr'] + attributes['finance_controlling'] + attributes['plant_finance_controlling'] + attributes['central_quality_management'] + attributes['apprenticeship_trainee_programs'] + attributes['other_central_support_functions'] + attributes['other_plant_support_functions']
        attributes['admin_in_of_net_sales'] = (attributes['admin'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['customer_service_plant'] = MOP.objects.filter(year=year, functional_area="SM11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['central_customer_service'] = MOP.objects.filter(year=year, functional_area="SM12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['marketing'] = MOP.objects.filter(year=year, functional_area="SM13").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['sales_force'] = MOP.objects.filter(year=year, functional_area="SM14").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['outbound_logistic_plant'] = MOP.objects.filter(year=year, functional_area="SM15").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['sales_logistic'] = MOP.objects.filter(year=year, functional_area="SM16").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['freight_out'] = MOP.objects.filter(year=year, functional_area="SM17").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="SM18").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="SM19").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['sales_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="SM26").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['other_sales_costs'] = MOP.objects.filter(year=year, functional_area="SM27").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['sales_income'] = MOP.objects.filter(year=year, functional_area="SM28").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['sales_managment'] = MOP.objects.filter(year=year, functional_area="SM29").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['sales_marketing'] = attributes['sales_managment'] + attributes['sales_income'] + attributes['other_sales_costs'] + attributes['sales_facility_costs_energy'] + attributes['target_gen_costs'] + attributes['target_poc'] + attributes['freight_out'] + attributes['sales_logistic'] + attributes['outbound_logistic_plant'] + attributes['sales_force'] + attributes['marketing'] + attributes['central_customer_service'] + attributes['customer_service_plant']
        attributes['sales_marketing_in_of_net_sales'] = (attributes['sales_marketing'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['general_rd_engineering_management_admin'] = MOP.objects.filter(year=year, functional_area="RD10").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['advanced_eng_innovation_mgt'] = MOP.objects.filter(year=year, functional_area="RD11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['engineering'] = MOP.objects.filter(year=year, functional_area="RD12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['platform_engineering_service'] = MOP.objects.filter(year=year, functional_area="RD13").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['rd_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="RD14").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['rd_tooling'] = MOP.objects.filter(year=year, functional_area="RD15").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['rd_system_engineering'] = MOP.objects.filter(year=year, functional_area="RD16").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['rd_target_gc'] = MOP.objects.filter(year=year, functional_area="RD17").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['product_management'] = MOP.objects.filter(year=year, functional_area="RD24").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['rd'] = attributes['product_management'] + attributes['rd_target_gc'] + attributes['rd_system_engineering'] + attributes['rd_tooling'] + attributes['rd_facility_costs_energy'] + attributes['platform_engineering_service'] + attributes['engineering'] + attributes['advanced_eng_innovation_mgt'] + attributes['general_rd_engineering_management_admin']
        attributes['rd_in_of_net_sales'] = (attributes['rd'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['primary_result'] = attributes['rd'] + attributes['sales_marketing'] + attributes['admin'] + attributes['gross_profit_operating_performance']
        attributes['primary_result_in_of_net_sales'] = (attributes['primary_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['intercompany_charges'] = MOP.objects.filter(year=year, functional_area="IC11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['ic_hq'] = attributes['intercompany_charges']
        attributes['ic_charges_in_of_net_sales'] = (attributes['ic_hq'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['other_plant'] = MOP.objects.filter(year=year, functional_area="OT01").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['other_general_costs'] = MOP.objects.filter(year=year, functional_area="OT02").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['customer_quality_campaigns'] = MOP.objects.filter(year=year, functional_area="OT03").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['other'] = attributes['customer_quality_campaigns'] + attributes['other_general_costs'] + attributes['other_plant']
        attributes['other_in_of_net_sales']  = (attributes['other'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['ebit'] = attributes['primary_result'] + attributes['other']
        attributes['ebit_in_of_net_sales'] = (attributes['ebit'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['interest_result'] = MOP.objects.filter(year=year, functional_area="FR11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['income_from_investments'] = MOP.objects.filter(year=year, functional_area="FR12").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['financial_result'] = attributes['interest_result'] + attributes['income_from_investments']
        attributes['financial_result_in_of_net_sales'] = (attributes['financial_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['pb_t'] = attributes['ebit'] + attributes['financial_result']
        attributes['ros_in'] = (attributes['pb_t'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['extraordinary_result'] = MOP.objects.filter(year=year, functional_area="EO11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['extraordinary_result_2'] = attributes['extraordinary_result']
        attributes['profit_loss_transfer'] = MOP.objects.filter(year=year, functional_area="PL11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['profit_loss_transfer_2'] = attributes['profit_loss_transfer']
        attributes['income_tax'] = MOP.objects.filter(year=year, functional_area="TX11").aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        attributes['income_tax_2'] = attributes['income_tax']
        attributes['company_result'] = attributes['pb_t'] + attributes['extraordinary_result_2'] + attributes['profit_loss_transfer_2'] + attributes['income_tax_2']
        attributes['own_production_operating_performance'] = attributes['gross_sales_own_production'] + attributes['inventory_change']

        Budget_Flexed_Costbook.objects.update_or_create(month=month, year=year, defaults=attributes)

    return HttpResponse("OK")


def Budget_Costbook_recalc(request=None, month=None, year=None):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
    else:
        if not year:
            year = 2021

    if not month:
        for i in range(1,13):
            attributes = {}
            attributes['gross_sales_merchandized_3p'] = MOP.objects.filter(year=year, functional_area="SA01").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['gross_sales_merchandized_ic'] = MOP.objects.filter(year=year, functional_area="SA02").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['gross_sales_merchandized'] = attributes['gross_sales_merchandized_3p'] + attributes['gross_sales_merchandized_ic']
            attributes['gross_sales_own_production_3p'] = MOP.objects.filter(year=year, functional_area="SA03").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['gross_sales_own_production_ic'] = MOP.objects.filter(year=year, functional_area="SA04").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['gross_sales_own_production'] = attributes['gross_sales_own_production_3p'] + attributes['gross_sales_own_production_ic']
            attributes['gross_sales'] = attributes['gross_sales_merchandized'] + attributes['gross_sales_own_production']
            attributes['customer_discounts'] = MOP.objects.filter(year=year, functional_area="OR11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['pricing_differences'] = MOP.objects.filter(year=year, functional_area="OR12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['royalties_licences_3p'] = MOP.objects.filter(year=year, functional_area="OR13").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['core_revenues'] = MOP.objects.filter(year=year, functional_area="OR14").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['income_from_scrap'] = MOP.objects.filter(year=year, functional_area="OR15").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['other_revenues'] = attributes['customer_discounts'] + attributes['pricing_differences'] + attributes['royalties_licences_3p'] + attributes['core_revenues'] + attributes['income_from_scrap']
            attributes['other_revenues_in_of_gross_sales'] = (attributes['other_revenues'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['net_sales'] = attributes['other_revenues'] + attributes['gross_sales']
            attributes['increase_decrease_of_finished_goods_wip_hk_1'] = MOP.objects.filter(year=year, functional_area="IN11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1'] = MOP.objects.filter(year=year, functional_area="IN12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['inventory_change'] = attributes['increase_decrease_of_finished_goods_wip_hk_1'] + attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1']
            attributes['self_constructed_assets'] = MOP.objects.filter(year=year, functional_area="OW11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['own_work_capitalized'] = attributes['self_constructed_assets']
            attributes['total_operating_performance'] = attributes['own_work_capitalized'] + attributes['inventory_change'] + attributes['net_sales']
            attributes['direct_production_material'] = MOP.objects.filter(year=year, functional_area="MD11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['merchandise_parts'] = MOP.objects.filter(year=year, functional_area="MD12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['sub_contracting'] = MOP.objects.filter(year=year, functional_area="MD13").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['excess_obsolete_stock'] = MOP.objects.filter(year=year, functional_area="MD14").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['scrap'] = MOP.objects.filter(year=year, functional_area="MD15").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['increase_decrease_of_finished_goods_wip'] = MOP.objects.filter(year=year, functional_area="MD16").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target'] = MOP.objects.filter(year=year, functional_area="MD17").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['inventory_shrink_and_revaluations'] = MOP.objects.filter(year=year, functional_area="MD18").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['material_direct'] = attributes['direct_production_material'] + attributes['merchandise_parts'] + attributes['sub_contracting'] + attributes['excess_obsolete_stock'] + attributes['scrap'] + attributes['increase_decrease_of_finished_goods_wip'] + attributes['target'] + attributes['inventory_shrink_and_revaluations']
            attributes['material_direct_in_of_gross_sales'] = (attributes['material_direct'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['material_direct_in_of_operating_performance'] = (attributes['material_direct'] / attributes['total_operating_performance']) if attributes['total_operating_performance'] else 0
            attributes['purchase_mat_di'] = MOP.objects.filter(year=year, functional_area="MO11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['tooling_supplier'] = MOP.objects.filter(year=year, functional_area="MO12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['procurement'] = MOP.objects.filter(year=year, functional_area="MO13").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['freight_in'] = MOP.objects.filter(year=year, functional_area="MO14").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['inbound_logistic'] = MOP.objects.filter(year=year, functional_area="MO15").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['quality_supplier'] = MOP.objects.filter(year=year, functional_area="MO16").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="MO17").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="MO18").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['material_overhead'] = attributes['target_gen_costs'] + attributes['target_poc'] + attributes['quality_supplier'] + attributes['inbound_logistic'] + attributes['freight_in'] + attributes['procurement'] + attributes['tooling_supplier'] + attributes['purchase_mat_di']
            attributes['material_overhead_in_of_gross_sales'] = (attributes['material_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['material_overhead_in_of_net_sales'] = (attributes['material_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['assembly_direct'] = MOP.objects.filter(year=year, functional_area="WD11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['machining_direct'] = MOP.objects.filter(year=year, functional_area="WD12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['pre_assembly_direct'] = MOP.objects.filter(year=year, functional_area="WD13").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['pre_machining_direct'] = MOP.objects.filter(year=year, functional_area="WD14").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['surface_treatment_direct'] = MOP.objects.filter(year=year, functional_area="WD15").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['other_direct_production_cost_centers_direct'] = MOP.objects.filter(year=year, functional_area="WD16").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['remanufacturing_direct'] = MOP.objects.filter(year=year, functional_area="WD17").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['welding_direct_production_direct'] = MOP.objects.filter(year=year, functional_area="WD18").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target_poc_direct'] = MOP.objects.filter(year=year, functional_area="WD19").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['direct_labour'] = attributes['target_poc_direct'] + attributes['welding_direct_production_direct'] + attributes['remanufacturing_direct'] + attributes['other_direct_production_cost_centers_direct'] + attributes['surface_treatment_direct'] + attributes['pre_machining_direct'] + attributes['pre_assembly_direct'] + attributes['machining_direct'] + attributes['assembly_direct']
            attributes['direct_labour_in_of_gross_sales'] = (attributes['direct_labour'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['direct_labour_in_of_net_sales'] = (attributes['direct_labour'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['direct_labour_in_of_sales_own_production'] = (attributes['direct_labour'] / attributes['gross_sales_own_production']) if attributes['gross_sales_own_production'] else 0
            attributes['assembly_overhead'] = MOP.objects.filter(year=year, functional_area="WO11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['machining_overhead'] = MOP.objects.filter(year=year, functional_area="WO12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['pre_assembly_overhead'] = MOP.objects.filter(year=year, functional_area="WO13").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['pre_machining_overhead'] = MOP.objects.filter(year=year, functional_area="WO14").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['surface_treatment_overhead'] = MOP.objects.filter(year=year, functional_area="WO15").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['other_direct_production_cost_centers_overhead'] = MOP.objects.filter(year=year, functional_area="WO16").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['remanufacturing_overhead'] = MOP.objects.filter(year=year, functional_area="WO17").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['welding_direct_production_overhead'] = MOP.objects.filter(year=year, functional_area="WO18").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['production_supply'] = MOP.objects.filter(year=year, functional_area="WO19").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['energy_utilities'] = MOP.objects.filter(year=year, functional_area="WO20").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['production_planning'] = MOP.objects.filter(year=year, functional_area="WO21").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['facility_costs'] = MOP.objects.filter(year=year, functional_area="WO22").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['maintenance_dept'] = MOP.objects.filter(year=year, functional_area="WO23").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['production_eng'] =MOP.objects.filter(year=year, functional_area="WO24").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['production_management'] = MOP.objects.filter(year=year, functional_area="WO25").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['quality_production'] = MOP.objects.filter(year=year, functional_area="WO26").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['quality_general'] = MOP.objects.filter(year=year, functional_area="WO27").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['purchasing_indirect_material'] = MOP.objects.filter(year=year, functional_area="WO28").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['warranty_plant'] = MOP.objects.filter(year=year, functional_area="WO29").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target_poc_overhead'] = MOP.objects.filter(year=year, functional_area="WO30").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="WO31").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['manufacturing_overhead'] = attributes['target_gen_costs'] + attributes['target_poc_overhead'] + attributes['warranty_plant'] + attributes['purchasing_indirect_material'] + attributes['quality_general'] + attributes['quality_production'] + attributes['production_management'] + attributes['production_eng'] + attributes['maintenance_dept'] + attributes['facility_costs'] + attributes['production_planning'] + attributes['energy_utilities'] + attributes['production_supply'] + attributes['welding_direct_production_overhead']  + attributes['remanufacturing_overhead'] + attributes['other_direct_production_cost_centers_overhead'] + attributes['surface_treatment_overhead'] + attributes['pre_machining_overhead'] + attributes['pre_assembly_overhead'] + attributes['machining_overhead'] + attributes['assembly_overhead']
            attributes['manufacturing_overhead_in_of_gross_sales'] = (attributes['manufacturing_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['manufacturing_overhead_in_of_net_sales'] = (attributes['manufacturing_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['hk_1'] = attributes['manufacturing_overhead'] + attributes['direct_labour'] + attributes['material_overhead'] + attributes['material_direct']
            attributes['gross_profit_operating_performance'] = attributes['hk_1'] + attributes['total_operating_performance']
            attributes['gross_profit_in_of_gross_sales'] = (attributes['gross_profit_operating_performance'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
            attributes['gross_profit_after_other_rev_in_of_net_sales'] = (attributes['gross_profit_operating_performance'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['general_management'] = MOP.objects.filter(year=year, functional_area="AD11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['plant_admin'] = MOP.objects.filter(year=year, functional_area="AD12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['central_functions'] = MOP.objects.filter(year=year, functional_area="AD13").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['central_function_indirect_purchasing'] = MOP.objects.filter(year=year, functional_area="AD14").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['information_technology'] = MOP.objects.filter(year=year, functional_area="AD15").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['admin_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="AD16").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['special_projects'] = MOP.objects.filter(year=year, functional_area="AD17").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="AD18").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="AD19").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['central_function_direct_purchasing'] = MOP.objects.filter(year=year, functional_area="AD21").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['central_function_industrial_engineering'] = MOP.objects.filter(year=year, functional_area="AD22").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['central_function_logistics'] = MOP.objects.filter(year=year, functional_area="AD23").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['hr'] = MOP.objects.filter(year=year, functional_area="AD24").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['plant_hr'] = MOP.objects.filter(year=year, functional_area="AD25").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['finance_controlling'] = MOP.objects.filter(year=year, functional_area="AD26").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['plant_finance_controlling'] = MOP.objects.filter(year=year, functional_area="AD27").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['central_quality_management'] = MOP.objects.filter(year=year, functional_area="AD28").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['apprenticeship_trainee_programs'] = MOP.objects.filter(year=year, functional_area="AD29").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['other_central_support_functions'] = MOP.objects.filter(year=year, functional_area="AD30").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['other_plant_support_functions'] = MOP.objects.filter(year=year, functional_area="AD31").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['admin'] = attributes['general_management'] + attributes['plant_admin'] + attributes['central_functions'] + attributes['central_function_indirect_purchasing'] + attributes['information_technology'] + attributes['admin_facility_costs_energy'] + attributes['special_projects'] + attributes['target_poc'] + attributes['target_gen_costs'] + attributes['central_function_direct_purchasing'] + attributes['central_function_industrial_engineering'] + attributes['central_function_logistics'] + attributes['hr'] + attributes['plant_hr'] + attributes['finance_controlling'] + attributes['plant_finance_controlling'] + attributes['central_quality_management'] + attributes['apprenticeship_trainee_programs'] + attributes['other_central_support_functions'] + attributes['other_plant_support_functions']
            attributes['admin_in_of_net_sales'] = (attributes['admin'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['customer_service_plant'] = MOP.objects.filter(year=year, functional_area="SM11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['central_customer_service'] = MOP.objects.filter(year=year, functional_area="SM12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['marketing'] = MOP.objects.filter(year=year, functional_area="SM13").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['sales_force'] = MOP.objects.filter(year=year, functional_area="SM14").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['outbound_logistic_plant'] = MOP.objects.filter(year=year, functional_area="SM15").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['sales_logistic'] = MOP.objects.filter(year=year, functional_area="SM16").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['freight_out'] = MOP.objects.filter(year=year, functional_area="SM17").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="SM18").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="SM19").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['sales_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="SM26").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['other_sales_costs'] = MOP.objects.filter(year=year, functional_area="SM27").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['sales_income'] = MOP.objects.filter(year=year, functional_area="SM28").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['sales_managment'] = MOP.objects.filter(year=year, functional_area="SM29").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['sales_marketing'] = attributes['sales_managment'] + attributes['sales_income'] + attributes['other_sales_costs'] + attributes['sales_facility_costs_energy'] + attributes['target_gen_costs'] + attributes['target_poc'] + attributes['freight_out'] + attributes['sales_logistic'] + attributes['outbound_logistic_plant'] + attributes['sales_force'] + attributes['marketing'] + attributes['central_customer_service'] + attributes['customer_service_plant']
            attributes['sales_marketing_in_of_net_sales'] = (attributes['sales_marketing'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['general_rd_engineering_management_admin'] = MOP.objects.filter(year=year, functional_area="RD10").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['advanced_eng_innovation_mgt'] = MOP.objects.filter(year=year, functional_area="RD11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['engineering'] = MOP.objects.filter(year=year, functional_area="RD12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['platform_engineering_service'] = MOP.objects.filter(year=year, functional_area="RD13").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['rd_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="RD14").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['rd_tooling'] = MOP.objects.filter(year=year, functional_area="RD15").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['rd_system_engineering'] = MOP.objects.filter(year=year, functional_area="RD16").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['rd_target_gc'] = MOP.objects.filter(year=year, functional_area="RD17").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['product_management'] = MOP.objects.filter(year=year, functional_area="RD24").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['rd'] = attributes['product_management'] + attributes['rd_target_gc'] + attributes['rd_system_engineering'] + attributes['rd_tooling'] + attributes['rd_facility_costs_energy'] + attributes['platform_engineering_service'] + attributes['engineering'] + attributes['advanced_eng_innovation_mgt'] + attributes['general_rd_engineering_management_admin']
            attributes['rd_in_of_net_sales'] = (attributes['rd'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['primary_result'] = attributes['rd'] + attributes['sales_marketing'] + attributes['admin'] + attributes['gross_profit_operating_performance']
            attributes['primary_result_in_of_net_sales'] = (attributes['primary_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['intercompany_charges'] = MOP.objects.filter(year=year, functional_area="IC11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['ic_hq'] = attributes['intercompany_charges']
            attributes['ic_charges_in_of_net_sales'] = (attributes['ic_hq'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['other_plant'] = MOP.objects.filter(year=year, functional_area="OT01").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
            attributes['other_general_costs'] = MOP.objects.filter(year=year, functional_area="OT02").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
            attributes['customer_quality_campaigns'] = MOP.objects.filter(year=year, functional_area="OT03").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
            attributes['other'] = attributes['customer_quality_campaigns'] + attributes['other_general_costs'] + attributes['other_plant']
            attributes['other_in_of_net_sales']  = (attributes['other'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['ebit'] = attributes['primary_result'] + attributes['other']
            attributes['ebit_in_of_net_sales'] = (attributes['ebit'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['interest_result'] = MOP.objects.filter(year=year, functional_area="FR11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['income_from_investments'] = MOP.objects.filter(year=year, functional_area="FR12").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['financial_result'] = attributes['interest_result'] + attributes['income_from_investments']
            attributes['financial_result_in_of_net_sales'] = (attributes['financial_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['pb_t'] = attributes['ebit'] + attributes['financial_result']
            attributes['ros_in'] = (attributes['pb_t'] / attributes['net_sales']) if attributes['net_sales'] else 0
            attributes['extraordinary_result'] = MOP.objects.filter(year=year, functional_area="EO11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['extraordinary_result_2'] = attributes['extraordinary_result']
            attributes['profit_loss_transfer'] = MOP.objects.filter(year=year, functional_area="PL11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['profit_loss_transfer_2'] = attributes['profit_loss_transfer']
            attributes['income_tax'] = MOP.objects.filter(year=year, functional_area="TX11").aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            attributes['income_tax_2'] = attributes['income_tax']
            attributes['company_result'] = attributes['pb_t'] + attributes['extraordinary_result_2'] + attributes['profit_loss_transfer_2'] + attributes['income_tax_2']
            attributes['own_production_operating_performance'] = attributes['gross_sales_own_production'] + attributes['inventory_change']

            Budget_Costbook.objects.update_or_create(month=i, year=year, defaults=attributes)
    else:
        attributes = {}
        attributes['gross_sales_merchandized_3p'] = MOP.objects.filter(year=year, functional_area="SA01").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['gross_sales_merchandized_ic'] = MOP.objects.filter(year=year, functional_area="SA02").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['gross_sales_merchandized'] = attributes['gross_sales_merchandized_3p'] + attributes['gross_sales_merchandized_ic']
        attributes['gross_sales_own_production_3p'] = MOP.objects.filter(year=year, functional_area="SA03").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['gross_sales_own_production_ic'] = MOP.objects.filter(year=year, functional_area="SA04").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['gross_sales_own_production'] = attributes['gross_sales_own_production_3p'] + attributes['gross_sales_own_production_ic']
        attributes['gross_sales'] = attributes['gross_sales_merchandized'] + attributes['gross_sales_own_production']
        attributes['customer_discounts'] = MOP.objects.filter(year=year, functional_area="OR11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['pricing_differences'] = MOP.objects.filter(year=year, functional_area="OR12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['royalties_licences_3p'] = MOP.objects.filter(year=year, functional_area="OR13").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['core_revenues'] = MOP.objects.filter(year=year, functional_area="OR14").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['income_from_scrap'] = MOP.objects.filter(year=year, functional_area="OR15").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['other_revenues'] = attributes['customer_discounts'] + attributes['pricing_differences'] + attributes['royalties_licences_3p'] + attributes['core_revenues'] + attributes['income_from_scrap']
        attributes['other_revenues_in_of_gross_sales'] = (attributes['other_revenues'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['net_sales'] = attributes['other_revenues'] + attributes['gross_sales']
        attributes['increase_decrease_of_finished_goods_wip_hk_1'] = MOP.objects.filter(year=year, functional_area="IN11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1'] = MOP.objects.filter(year=year, functional_area="IN12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['inventory_change'] = attributes['increase_decrease_of_finished_goods_wip_hk_1'] + attributes['increase_decrease_of_finished_goods_wip_eng_non_hk_1']
        attributes['self_constructed_assets'] = MOP.objects.filter(year=year, functional_area="OW11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['own_work_capitalized'] = attributes['self_constructed_assets']
        attributes['total_operating_performance'] = attributes['own_work_capitalized'] + attributes['inventory_change'] + attributes['net_sales']
        attributes['direct_production_material'] = MOP.objects.filter(year=year, functional_area="MD11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['merchandise_parts'] = MOP.objects.filter(year=year, functional_area="MD12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['sub_contracting'] = MOP.objects.filter(year=year, functional_area="MD13").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['excess_obsolete_stock'] = MOP.objects.filter(year=year, functional_area="MD14").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['scrap'] = MOP.objects.filter(year=year, functional_area="MD15").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['increase_decrease_of_finished_goods_wip'] = MOP.objects.filter(year=year, functional_area="MD16").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target'] = MOP.objects.filter(year=year, functional_area="MD17").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['inventory_shrink_and_revaluations'] = MOP.objects.filter(year=year, functional_area="MD18").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['material_direct'] = attributes['direct_production_material'] + attributes['merchandise_parts'] + attributes['sub_contracting'] + attributes['excess_obsolete_stock'] + attributes['scrap'] + attributes['increase_decrease_of_finished_goods_wip'] + attributes['target'] + attributes['inventory_shrink_and_revaluations']
        attributes['material_direct_in_of_gross_sales'] = (attributes['material_direct'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['material_direct_in_of_operating_performance'] = (attributes['material_direct'] / attributes['total_operating_performance']) if attributes['total_operating_performance'] else 0
        attributes['purchase_mat_di'] = MOP.objects.filter(year=year, functional_area="MO11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['tooling_supplier'] = MOP.objects.filter(year=year, functional_area="MO12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['procurement'] = MOP.objects.filter(year=year, functional_area="MO13").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['freight_in'] = MOP.objects.filter(year=year, functional_area="MO14").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['inbound_logistic'] = MOP.objects.filter(year=year, functional_area="MO15").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['quality_supplier'] = MOP.objects.filter(year=year, functional_area="MO16").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="MO17").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="MO18").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['material_overhead'] = attributes['target_gen_costs'] + attributes['target_poc'] + attributes['quality_supplier'] + attributes['inbound_logistic'] + attributes['freight_in'] + attributes['procurement'] + attributes['tooling_supplier'] + attributes['purchase_mat_di']
        attributes['material_overhead_in_of_gross_sales'] = (attributes['material_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['material_overhead_in_of_net_sales'] = (attributes['material_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['assembly_direct'] = MOP.objects.filter(year=year, functional_area="WD11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['machining_direct'] = MOP.objects.filter(year=year, functional_area="WD12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['pre_assembly_direct'] = MOP.objects.filter(year=year, functional_area="WD13").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['pre_machining_direct'] = MOP.objects.filter(year=year, functional_area="WD14").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['surface_treatment_direct'] = MOP.objects.filter(year=year, functional_area="WD15").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['other_direct_production_cost_centers_direct'] = MOP.objects.filter(year=year, functional_area="WD16").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['remanufacturing_direct'] = MOP.objects.filter(year=year, functional_area="WD17").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['welding_direct_production_direct'] = MOP.objects.filter(year=year, functional_area="WD18").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target_poc_direct'] = MOP.objects.filter(year=year, functional_area="WD19").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['direct_labour'] = attributes['target_poc_direct'] + attributes['welding_direct_production_direct'] + attributes['remanufacturing_direct'] + attributes['other_direct_production_cost_centers_direct'] + attributes['surface_treatment_direct'] + attributes['pre_machining_direct'] + attributes['pre_assembly_direct'] + attributes['machining_direct'] + attributes['assembly_direct']
        attributes['direct_labour_in_of_gross_sales'] = (attributes['direct_labour'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['direct_labour_in_of_net_sales'] = (attributes['direct_labour'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['direct_labour_in_of_sales_own_production'] = (attributes['direct_labour'] / attributes['gross_sales_own_production']) if attributes['gross_sales_own_production'] else 0
        attributes['assembly_overhead'] = MOP.objects.filter(year=year, functional_area="WO11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['machining_overhead'] = MOP.objects.filter(year=year, functional_area="WO12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['pre_assembly_overhead'] = MOP.objects.filter(year=year, functional_area="WO13").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['pre_machining_overhead'] = MOP.objects.filter(year=year, functional_area="WO14").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['surface_treatment_overhead'] = MOP.objects.filter(year=year, functional_area="WO15").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['other_direct_production_cost_centers_overhead'] = MOP.objects.filter(year=year, functional_area="WO16").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['remanufacturing_overhead'] = MOP.objects.filter(year=year, functional_area="WO17").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['welding_direct_production_overhead'] = MOP.objects.filter(year=year, functional_area="WO18").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['production_supply'] = MOP.objects.filter(year=year, functional_area="WO19").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['energy_utilities'] = MOP.objects.filter(year=year, functional_area="WO20").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['production_planning'] = MOP.objects.filter(year=year, functional_area="WO21").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['facility_costs'] = MOP.objects.filter(year=year, functional_area="WO22").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['maintenance_dept'] = MOP.objects.filter(year=year, functional_area="WO23").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['production_eng'] =MOP.objects.filter(year=year, functional_area="WO24").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['production_management'] = MOP.objects.filter(year=year, functional_area="WO25").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['quality_production'] = MOP.objects.filter(year=year, functional_area="WO26").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['quality_general'] = MOP.objects.filter(year=year, functional_area="WO27").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['purchasing_indirect_material'] = MOP.objects.filter(year=year, functional_area="WO28").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['warranty_plant'] = MOP.objects.filter(year=year, functional_area="WO29").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target_poc_overhead'] = MOP.objects.filter(year=year, functional_area="WO30").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="WO31").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['manufacturing_overhead'] = attributes['target_gen_costs'] + attributes['target_poc_overhead'] + attributes['warranty_plant'] + attributes['purchasing_indirect_material'] + attributes['quality_general'] + attributes['quality_production'] + attributes['production_management'] + attributes['production_eng'] + attributes['maintenance_dept'] + attributes['facility_costs'] + attributes['production_planning'] + attributes['energy_utilities'] + attributes['production_supply'] + attributes['welding_direct_production_overhead']  + attributes['remanufacturing_overhead'] + attributes['other_direct_production_cost_centers_overhead'] + attributes['surface_treatment_overhead'] + attributes['pre_machining_overhead'] + attributes['pre_assembly_overhead'] + attributes['machining_overhead'] + attributes['assembly_overhead']
        attributes['manufacturing_overhead_in_of_gross_sales'] = (attributes['manufacturing_overhead'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['manufacturing_overhead_in_of_net_sales'] = (attributes['manufacturing_overhead'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['hk_1'] = attributes['manufacturing_overhead'] + attributes['direct_labour'] + attributes['material_overhead'] + attributes['material_direct']
        attributes['gross_profit_operating_performance'] = attributes['hk_1'] + attributes['total_operating_performance']
        attributes['gross_profit_in_of_gross_sales'] = (attributes['gross_profit_operating_performance'] / attributes['gross_sales']) if attributes['gross_sales'] else 0
        attributes['gross_profit_after_other_rev_in_of_net_sales'] = (attributes['gross_profit_operating_performance'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['general_management'] = MOP.objects.filter(year=year, functional_area="AD11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['plant_admin'] = MOP.objects.filter(year=year, functional_area="AD12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['central_functions'] = MOP.objects.filter(year=year, functional_area="AD13").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['central_function_indirect_purchasing'] = MOP.objects.filter(year=year, functional_area="AD14").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['information_technology'] = MOP.objects.filter(year=year, functional_area="AD15").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['admin_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="AD16").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['special_projects'] = MOP.objects.filter(year=year, functional_area="AD17").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="AD18").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="AD19").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['central_function_direct_purchasing'] = MOP.objects.filter(year=year, functional_area="AD21").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['central_function_industrial_engineering'] = MOP.objects.filter(year=year, functional_area="AD22").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['central_function_logistics'] = MOP.objects.filter(year=year, functional_area="AD23").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['hr'] = MOP.objects.filter(year=year, functional_area="AD24").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['plant_hr'] = MOP.objects.filter(year=year, functional_area="AD25").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['finance_controlling'] = MOP.objects.filter(year=year, functional_area="AD26").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['plant_finance_controlling'] = MOP.objects.filter(year=year, functional_area="AD27").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['central_quality_management'] = MOP.objects.filter(year=year, functional_area="AD28").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['apprenticeship_trainee_programs'] = MOP.objects.filter(year=year, functional_area="AD29").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['other_central_support_functions'] = MOP.objects.filter(year=year, functional_area="AD30").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['other_plant_support_functions'] = MOP.objects.filter(year=year, functional_area="AD31").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['admin'] = attributes['general_management'] + attributes['plant_admin'] + attributes['central_functions'] + attributes['central_function_indirect_purchasing'] + attributes['information_technology'] + attributes['admin_facility_costs_energy'] + attributes['special_projects'] + attributes['target_poc'] + attributes['target_gen_costs'] + attributes['central_function_direct_purchasing'] + attributes['central_function_industrial_engineering'] + attributes['central_function_logistics'] + attributes['hr'] + attributes['plant_hr'] + attributes['finance_controlling'] + attributes['plant_finance_controlling'] + attributes['central_quality_management'] + attributes['apprenticeship_trainee_programs'] + attributes['other_central_support_functions'] + attributes['other_plant_support_functions']
        attributes['admin_in_of_net_sales'] = (attributes['admin'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['customer_service_plant'] = MOP.objects.filter(year=year, functional_area="SM11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['central_customer_service'] = MOP.objects.filter(year=year, functional_area="SM12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['marketing'] = MOP.objects.filter(year=year, functional_area="SM13").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['sales_force'] = MOP.objects.filter(year=year, functional_area="SM14").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['outbound_logistic_plant'] = MOP.objects.filter(year=year, functional_area="SM15").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['sales_logistic'] = MOP.objects.filter(year=year, functional_area="SM16").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['freight_out'] = MOP.objects.filter(year=year, functional_area="SM17").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target_poc'] = MOP.objects.filter(year=year, functional_area="SM18").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['target_gen_costs'] = MOP.objects.filter(year=year, functional_area="SM19").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['sales_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="SM26").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['other_sales_costs'] = MOP.objects.filter(year=year, functional_area="SM27").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['sales_income'] = MOP.objects.filter(year=year, functional_area="SM28").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['sales_managment'] = MOP.objects.filter(year=year, functional_area="SM29").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['sales_marketing'] = attributes['sales_managment'] + attributes['sales_income'] + attributes['other_sales_costs'] + attributes['sales_facility_costs_energy'] + attributes['target_gen_costs'] + attributes['target_poc'] + attributes['freight_out'] + attributes['sales_logistic'] + attributes['outbound_logistic_plant'] + attributes['sales_force'] + attributes['marketing'] + attributes['central_customer_service'] + attributes['customer_service_plant']
        attributes['sales_marketing_in_of_net_sales'] = (attributes['sales_marketing'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['general_rd_engineering_management_admin'] = MOP.objects.filter(year=year, functional_area="RD10").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['advanced_eng_innovation_mgt'] = MOP.objects.filter(year=year, functional_area="RD11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['engineering'] = MOP.objects.filter(year=year, functional_area="RD12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['platform_engineering_service'] = MOP.objects.filter(year=year, functional_area="RD13").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['rd_facility_costs_energy'] = MOP.objects.filter(year=year, functional_area="RD14").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['rd_tooling'] = MOP.objects.filter(year=year, functional_area="RD15").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['rd_system_engineering'] = MOP.objects.filter(year=year, functional_area="RD16").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['rd_target_gc'] = MOP.objects.filter(year=year, functional_area="RD17").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['product_management'] = MOP.objects.filter(year=year, functional_area="RD24").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['rd'] = attributes['product_management'] + attributes['rd_target_gc'] + attributes['rd_system_engineering'] + attributes['rd_tooling'] + attributes['rd_facility_costs_energy'] + attributes['platform_engineering_service'] + attributes['engineering'] + attributes['advanced_eng_innovation_mgt'] + attributes['general_rd_engineering_management_admin']
        attributes['rd_in_of_net_sales'] = (attributes['rd'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['primary_result'] = attributes['rd'] + attributes['sales_marketing'] + attributes['admin'] + attributes['gross_profit_operating_performance']
        attributes['primary_result_in_of_net_sales'] = (attributes['primary_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['intercompany_charges'] = MOP.objects.filter(year=year, functional_area="IC11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['ic_hq'] = attributes['intercompany_charges']
        attributes['ic_charges_in_of_net_sales'] = (attributes['ic_hq'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['other_plant'] = MOP.objects.filter(year=year, functional_area="OT01").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['other_general_costs'] = MOP.objects.filter(year=year, functional_area="OT02").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['customer_quality_campaigns'] = MOP.objects.filter(year=year, functional_area="OT03").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['other'] = attributes['customer_quality_campaigns'] + attributes['other_general_costs'] + attributes['other_plant']
        attributes['other_in_of_net_sales']  = (attributes['other'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['ebit'] = attributes['primary_result'] + attributes['other']
        attributes['ebit_in_of_net_sales'] = (attributes['ebit'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['interest_result'] = MOP.objects.filter(year=year, functional_area="FR11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['income_from_investments'] = MOP.objects.filter(year=year, functional_area="FR12").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['financial_result'] = attributes['interest_result'] + attributes['income_from_investments']
        attributes['financial_result_in_of_net_sales'] = (attributes['financial_result'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['pb_t'] = attributes['ebit'] + attributes['financial_result']
        attributes['ros_in'] = (attributes['pb_t'] / attributes['net_sales']) if attributes['net_sales'] else 0
        attributes['extraordinary_result'] = MOP.objects.filter(year=year, functional_area="EO11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['extraordinary_result_2'] = attributes['extraordinary_result']
        attributes['profit_loss_transfer'] = MOP.objects.filter(year=year, functional_area="PL11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['profit_loss_transfer_2'] = attributes['profit_loss_transfer']
        attributes['income_tax'] = MOP.objects.filter(year=year, functional_area="TX11").aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        attributes['income_tax_2'] = attributes['income_tax']
        attributes['company_result'] = attributes['pb_t'] + attributes['extraordinary_result_2'] + attributes['profit_loss_transfer_2'] + attributes['income_tax_2']
        attributes['own_production_operating_performance'] = attributes['gross_sales_own_production'] + attributes['inventory_change']

        Budget_Costbook.objects.update_or_create(month=month, year=year, defaults=attributes)

    return HttpResponse("OK")


def sendmail(request=None, message_content=None, subject=None, recipient='peter.vajda@knorr-bremse.com', cc='peter.vajda@knorr-bremse.com'):

    if request:
        message_content = request.GET.get('message_content')
        subject = request.GET.get('subject')
        recipient = request.GET.get('recipient')

    msg = EmailMessage()

    msg['Subject'] = subject
    msg['From'] = "automat@knorr-bremse.com"
    msg['To'] = recipient
    msg['Cc'] = cc
    msg.set_content(message_content, subtype='html')


    s = smtplib.SMTP('smtp-relay.corp.knorr-bremse.com')
    s.send_message(msg)
    s.quit()


def Budget_Budget_recalc(request=None, month=None, year=None):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
    else:
        if not year:
            year = 2021
    
    if not month:
        for i in range(1,13):
            own_production = MOP.objects.filter(year=year, cost_position=1).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            merchandise = MOP.objects.filter(year=year, cost_position=2).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            other_sales = MOP.objects.filter(year=year, cost_position=48).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            sales_discounts = MOP.objects.filter(year=year, cost_position=3).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            net_sales = own_production + merchandise + other_sales + sales_discounts
            work_in_progress = MOP.objects.filter(year=year, cost_position=4).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            other_operating_income = MOP.objects.filter(year=year, cost_position=5).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            revenues_total = net_sales + work_in_progress + other_operating_income
            foreign_exchange_gains = MOP.objects.filter(year=year, cost_position=7).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            sundry_operating_income_expense = MOP.objects.filter(year=year, cost_position=8).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
            ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
            material_direct = MOP.objects.filter(year=year, cost_position=10).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
            oils_and_lubricants = MOP.objects.filter(year=year, cost_position=11).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            energy_costs = MOP.objects.filter(year=year, cost_position=12).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            tools = MOP.objects.filter(year=year, cost_position=13).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            spare_parts = MOP.objects.filter(year=year, cost_position=14).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            packaging = MOP.objects.filter(year=year, cost_position=15).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            other_overhead_material = MOP.objects.filter(year=year, cost_position=16).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            storage_fees_and_freight_in = MOP.objects.filter(year=year, cost_position=17).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
            oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
            cost_of_goods_sold = MOP.objects.filter(year=year, cost_position=19).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
            discounts_from_suppliers = MOP.objects.filter(year=year, cost_position=20).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
            material_vs_total_revenues = material / revenues_total if revenues_total else 0
            direct_wages = MOP.objects.filter(year=year, cost_position=22).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            personal_costs_indirect_salaried = MOP.objects.filter(year=year, cost_position=23).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            personal_costs = direct_wages + personal_costs_indirect_salaried
            personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
            depreciation = MOP.objects.filter(year=year, cost_position=25).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
            repairs_and_maintenance = MOP.objects.filter(year=year, cost_position=26).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            provision_for_repairs_and_maintenance = MOP.objects.filter(year=year, cost_position=27).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            freight_out = MOP.objects.filter(year=year, cost_position=28).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            telecommunication_fees = MOP.objects.filter(year=year, cost_position=29).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            warranty_claims = MOP.objects.filter(year=year, cost_position=30).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            advisory_services = MOP.objects.filter(year=year, cost_position=31).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            advertising = MOP.objects.filter(year=year, cost_position=32).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            other_external_services = MOP.objects.filter(year=year, cost_position=33).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            travel_expense = MOP.objects.filter(year=year, cost_position=34).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            low_value_assets = MOP.objects.filter(year=year, cost_position=35).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            taxes_and_fees = MOP.objects.filter(year=year, cost_position=36).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            rent_and_leasing = MOP.objects.filter(year=year, cost_position=37).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            sold_fixed_assets = MOP.objects.filter(year=year, cost_position=38).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            foreign_exchange_losses = MOP.objects.filter(year=year, cost_position=39).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            training = MOP.objects.filter(year=year, cost_position=40).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            provision_for_general_risks = MOP.objects.filter(year=year, cost_position=41).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            insurance = MOP.objects.filter(year=year, cost_position=42).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            other_group_charges = MOP.objects.filter(year=year, cost_position=49).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            management_fees = MOP.objects.filter(year=year, cost_position=43).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            other_expenses = MOP.objects.filter(year=year, cost_position=44).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
            ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
            interests = MOP.objects.filter(year=year, cost_position=46).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            ebit = revenues_total + other_operating_income + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
            ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
            income_tax = MOP.objects.filter(year=year, cost_position=50).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            profit_after_tax = ebit + income_tax + interests
            profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

            Budget_Budget.objects.update_or_create(month=i, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    return HttpResponse('okay')


def Budget_Flexed_Budget_recalc(request=None, month=None, year=None):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
    else:
        if not year:
            year = 2021
    
    if not month:
        for i in range(1,13):
            own_production = MOP.objects.filter(year=year, cost_position=1).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            merchandise = MOP.objects.filter(year=year, cost_position=2).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            other_sales = MOP.objects.filter(year=year, cost_position=48).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            sales_discounts = MOP.objects.filter(year=year, cost_position=3).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            net_sales = own_production + merchandise + other_sales + sales_discounts
            work_in_progress = MOP.objects.filter(year=year, cost_position=4).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            other_operating_income = MOP.objects.filter(year=year, cost_position=5).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            revenues_total = net_sales + work_in_progress + other_operating_income
            foreign_exchange_gains = MOP.objects.filter(year=year, cost_position=7).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            sundry_operating_income_expense = MOP.objects.filter(year=year, cost_position=8).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
            ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
            material_direct = MOP.objects.filter(year=year, cost_position=10).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
            oils_and_lubricants = MOP.objects.filter(year=year, cost_position=11).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            energy_costs = MOP.objects.filter(year=year, cost_position=12).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            tools = MOP.objects.filter(year=year, cost_position=13).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            spare_parts = MOP.objects.filter(year=year, cost_position=14).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            packaging = MOP.objects.filter(year=year, cost_position=15).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            other_overhead_material = MOP.objects.filter(year=year, cost_position=16).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            storage_fees_and_freight_in = MOP.objects.filter(year=year, cost_position=17).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
            oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
            cost_of_goods_sold = MOP.objects.filter(year=year, cost_position=19).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
            discounts_from_suppliers = MOP.objects.filter(year=year, cost_position=20).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
            material_vs_total_revenues = material / revenues_total if revenues_total else 0
            direct_wages = MOP.objects.filter(year=year, cost_position=22).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            personal_costs_indirect_salaried = MOP.objects.filter(year=year, cost_position=23).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            personal_costs = direct_wages + personal_costs_indirect_salaried
            personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
            depreciation = MOP.objects.filter(year=year, cost_position=25).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
            repairs_and_maintenance = MOP.objects.filter(year=year, cost_position=26).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            provision_for_repairs_and_maintenance = MOP.objects.filter(year=year, cost_position=27).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            freight_out = MOP.objects.filter(year=year, cost_position=28).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            telecommunication_fees = MOP.objects.filter(year=year, cost_position=29).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            warranty_claims = MOP.objects.filter(year=year, cost_position=30).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            advisory_services = MOP.objects.filter(year=year, cost_position=31).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            advertising = MOP.objects.filter(year=year, cost_position=32).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            other_external_services = MOP.objects.filter(year=year, cost_position=33).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            travel_expense = MOP.objects.filter(year=year, cost_position=34).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            low_value_assets = MOP.objects.filter(year=year, cost_position=35).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            taxes_and_fees = MOP.objects.filter(year=year, cost_position=36).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            rent_and_leasing = MOP.objects.filter(year=year, cost_position=37).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            sold_fixed_assets = MOP.objects.filter(year=year, cost_position=38).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            foreign_exchange_losses = MOP.objects.filter(year=year, cost_position=39).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            training = MOP.objects.filter(year=year, cost_position=40).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            provision_for_general_risks = MOP.objects.filter(year=year, cost_position=41).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            insurance = MOP.objects.filter(year=year, cost_position=42).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            other_group_charges = MOP.objects.filter(year=year, cost_position=49).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            management_fees = MOP.objects.filter(year=year, cost_position=43).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            other_expenses = MOP.objects.filter(year=year, cost_position=44).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
            ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
            interests = MOP.objects.filter(year=year, cost_position=46).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
            ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
            income_tax = MOP.objects.filter(year=year, cost_position=50).aggregate(actual_value=Sum(f'flexed_budget_month_{i}'))['actual_value'] or 0
            profit_after_tax = ebit + income_tax + interests
            profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

            Budget_Flexed_Budget.objects.update_or_create(month=i, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    else:
        own_production = MOP.objects.filter(year=year, cost_position=1).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        merchandise = MOP.objects.filter(year=year, cost_position=2).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        other_sales = MOP.objects.filter(year=year, cost_position=48).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        sales_discounts = MOP.objects.filter(year=year, cost_position=3).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        net_sales = own_production + merchandise + other_sales + sales_discounts
        print(net_sales)
        work_in_progress = MOP.objects.filter(year=year, cost_position=4).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        other_operating_income = MOP.objects.filter(year=year, cost_position=5).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        revenues_total = net_sales + work_in_progress + other_operating_income
        foreign_exchange_gains = MOP.objects.filter(year=year, cost_position=7).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        sundry_operating_income_expense = MOP.objects.filter(year=year, cost_position=8).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
        ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
        material_direct = MOP.objects.filter(year=year, cost_position=10).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
        oils_and_lubricants = MOP.objects.filter(year=year, cost_position=11).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        energy_costs = MOP.objects.filter(year=year, cost_position=12).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        tools = MOP.objects.filter(year=year, cost_position=13).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        spare_parts = MOP.objects.filter(year=year, cost_position=14).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        packaging = MOP.objects.filter(year=year, cost_position=15).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        other_overhead_material = MOP.objects.filter(year=year, cost_position=16).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        storage_fees_and_freight_in = MOP.objects.filter(year=year, cost_position=17).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
        oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
        cost_of_goods_sold = MOP.objects.filter(year=year, cost_position=19).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
        discounts_from_suppliers = MOP.objects.filter(year=year, cost_position=20).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
        material_vs_total_revenues = material / revenues_total if revenues_total else 0
        direct_wages = MOP.objects.filter(year=year, cost_position=22).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        personal_costs_indirect_salaried = MOP.objects.filter(year=year, cost_position=23).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        personal_costs = direct_wages + personal_costs_indirect_salaried
        personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
        depreciation = MOP.objects.filter(year=year, cost_position=25).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
        repairs_and_maintenance = MOP.objects.filter(year=year, cost_position=26).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        provision_for_repairs_and_maintenance = MOP.objects.filter(year=year, cost_position=27).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        freight_out = MOP.objects.filter(year=year, cost_position=28).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        telecommunication_fees = MOP.objects.filter(year=year, cost_position=29).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        warranty_claims = MOP.objects.filter(year=year, cost_position=30).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        advisory_services = MOP.objects.filter(year=year, cost_position=31).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        advertising = MOP.objects.filter(year=year, cost_position=32).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        other_external_services = MOP.objects.filter(year=year, cost_position=33).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        travel_expense = MOP.objects.filter(year=year, cost_position=34).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        low_value_assets = MOP.objects.filter(year=year, cost_position=35).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        taxes_and_fees = MOP.objects.filter(year=year, cost_position=36).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        rent_and_leasing = MOP.objects.filter(year=year, cost_position=37).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        sold_fixed_assets = MOP.objects.filter(year=year, cost_position=38).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        foreign_exchange_losses = MOP.objects.filter(year=year, cost_position=39).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        training = MOP.objects.filter(year=year, cost_position=40).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        provision_for_general_risks = MOP.objects.filter(year=year, cost_position=41).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        insurance = MOP.objects.filter(year=year, cost_position=42).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        other_group_charges = MOP.objects.filter(year=year, cost_position=49).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        management_fees = MOP.objects.filter(year=year, cost_position=43).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        other_expenses = MOP.objects.filter(year=year, cost_position=44).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
        ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
        interests = MOP.objects.filter(year=year, cost_position=46).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
        ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
        income_tax = MOP.objects.filter(year=year, cost_position=50).aggregate(actual_value=Sum(f'flexed_budget_month_{month}'))['actual_value'] or 0
        profit_after_tax = ebit + income_tax + interests
        profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

        Budget_Flexed_Budget.objects.update_or_create(month=month, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    return HttpResponse("Budget_Flexed_Budget_recalc OK")


def Budget_Outlook_Flexed_recalc(request=None, month=None, year=None):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
    else:
        if not year:
            year = 2021
    
    if not month:
        for i in range(1,13):
            own_production = MOP_Outlook.objects.filter(year=year, cost_position=1).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            merchandise = MOP_Outlook.objects.filter(year=year, cost_position=2).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            other_sales = MOP_Outlook.objects.filter(year=year, cost_position=48).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            sales_discounts = MOP_Outlook.objects.filter(year=year, cost_position=3).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            net_sales = own_production + merchandise + other_sales + sales_discounts
            work_in_progress = MOP_Outlook.objects.filter(year=year, cost_position=4).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            other_operating_income = MOP_Outlook.objects.filter(year=year, cost_position=5).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            revenues_total = net_sales + work_in_progress + other_operating_income
            foreign_exchange_gains = MOP_Outlook.objects.filter(year=year, cost_position=7).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            sundry_operating_income_expense = MOP_Outlook.objects.filter(year=year, cost_position=8).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
            ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
            material_direct = MOP_Outlook.objects.filter(year=year, cost_position=10).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
            oils_and_lubricants = MOP_Outlook.objects.filter(year=year, cost_position=11).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            energy_costs = MOP_Outlook.objects.filter(year=year, cost_position=12).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            tools = MOP_Outlook.objects.filter(year=year, cost_position=13).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            spare_parts = MOP_Outlook.objects.filter(year=year, cost_position=14).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            packaging = MOP_Outlook.objects.filter(year=year, cost_position=15).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            other_overhead_material = MOP_Outlook.objects.filter(year=year, cost_position=16).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            storage_fees_and_freight_in = MOP_Outlook.objects.filter(year=year, cost_position=17).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
            oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
            cost_of_goods_sold = MOP_Outlook.objects.filter(year=year, cost_position=19).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
            discounts_from_suppliers = MOP_Outlook.objects.filter(year=year, cost_position=20).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
            material_vs_total_revenues = material / revenues_total if revenues_total else 0
            direct_wages = MOP_Outlook.objects.filter(year=year, cost_position=22).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            personal_costs_indirect_salaried = MOP_Outlook.objects.filter(year=year, cost_position=23).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            personal_costs = direct_wages + personal_costs_indirect_salaried
            personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
            depreciation = MOP_Outlook.objects.filter(year=year, cost_position=25).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
            repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=26).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            provision_for_repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=27).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            freight_out = MOP_Outlook.objects.filter(year=year, cost_position=28).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            telecommunication_fees = MOP_Outlook.objects.filter(year=year, cost_position=29).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            warranty_claims = MOP_Outlook.objects.filter(year=year, cost_position=30).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            advisory_services = MOP_Outlook.objects.filter(year=year, cost_position=31).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            advertising = MOP_Outlook.objects.filter(year=year, cost_position=32).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            other_external_services = MOP_Outlook.objects.filter(year=year, cost_position=33).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            travel_expense = MOP_Outlook.objects.filter(year=year, cost_position=34).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            low_value_assets = MOP_Outlook.objects.filter(year=year, cost_position=35).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            taxes_and_fees = MOP_Outlook.objects.filter(year=year, cost_position=36).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            rent_and_leasing = MOP_Outlook.objects.filter(year=year, cost_position=37).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            sold_fixed_assets = MOP_Outlook.objects.filter(year=year, cost_position=38).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            foreign_exchange_losses = MOP_Outlook.objects.filter(year=year, cost_position=39).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            training = MOP_Outlook.objects.filter(year=year, cost_position=40).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            provision_for_general_risks = MOP_Outlook.objects.filter(year=year, cost_position=41).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            insurance = MOP_Outlook.objects.filter(year=year, cost_position=42).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            other_group_charges = MOP_Outlook.objects.filter(year=year, cost_position=49).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            management_fees = MOP_Outlook.objects.filter(year=year, cost_position=43).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            other_expenses = MOP_Outlook.objects.filter(year=year, cost_position=44).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
            ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
            interests = MOP_Outlook.objects.filter(year=year, cost_position=46).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
            ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
            income_tax = MOP_Outlook.objects.filter(year=year, cost_position=50).aggregate(actual_value=Sum(f'flexed_outlook_{i}'))['actual_value'] or 0
            profit_after_tax = ebit + income_tax + interests
            profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

            Budget_Outlook_Flexed.objects.update_or_create(month=i, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    else:
        own_production = MOP_Outlook.objects.filter(year=year, cost_position=1).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        merchandise = MOP_Outlook.objects.filter(year=year, cost_position=2).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        other_sales = MOP_Outlook.objects.filter(year=year, cost_position=48).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        sales_discounts = MOP_Outlook.objects.filter(year=year, cost_position=3).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        net_sales = own_production + merchandise + other_sales + sales_discounts
        work_in_progress = MOP_Outlook.objects.filter(year=year, cost_position=4).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        other_operating_income = MOP_Outlook.objects.filter(year=year, cost_position=5).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        revenues_total = net_sales + work_in_progress + other_operating_income
        foreign_exchange_gains = MOP_Outlook.objects.filter(year=year, cost_position=7).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        sundry_operating_income_expense = MOP_Outlook.objects.filter(year=year, cost_position=8).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
        ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
        material_direct = MOP_Outlook.objects.filter(year=year, cost_position=10).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
        oils_and_lubricants = MOP_Outlook.objects.filter(year=year, cost_position=11).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        energy_costs = MOP_Outlook.objects.filter(year=year, cost_position=12).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        tools = MOP_Outlook.objects.filter(year=year, cost_position=13).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        spare_parts = MOP_Outlook.objects.filter(year=year, cost_position=14).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        packaging = MOP_Outlook.objects.filter(year=year, cost_position=15).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        other_overhead_material = MOP_Outlook.objects.filter(year=year, cost_position=16).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        storage_fees_and_freight_in = MOP_Outlook.objects.filter(year=year, cost_position=17).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
        oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
        cost_of_goods_sold = MOP_Outlook.objects.filter(year=year, cost_position=19).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
        discounts_from_suppliers = MOP_Outlook.objects.filter(year=year, cost_position=20).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
        material_vs_total_revenues = material / revenues_total if revenues_total else 0
        direct_wages = MOP_Outlook.objects.filter(year=year, cost_position=22).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        personal_costs_indirect_salaried = MOP_Outlook.objects.filter(year=year, cost_position=23).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        personal_costs = direct_wages + personal_costs_indirect_salaried
        personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
        depreciation = MOP_Outlook.objects.filter(year=year, cost_position=25).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
        repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=26).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        provision_for_repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=27).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        freight_out = MOP_Outlook.objects.filter(year=year, cost_position=28).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        telecommunication_fees = MOP_Outlook.objects.filter(year=year, cost_position=29).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        warranty_claims = MOP_Outlook.objects.filter(year=year, cost_position=30).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        advisory_services = MOP_Outlook.objects.filter(year=year, cost_position=31).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        advertising = MOP_Outlook.objects.filter(year=year, cost_position=32).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        other_external_services = MOP_Outlook.objects.filter(year=year, cost_position=33).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        travel_expense = MOP_Outlook.objects.filter(year=year, cost_position=34).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        low_value_assets = MOP_Outlook.objects.filter(year=year, cost_position=35).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        taxes_and_fees = MOP_Outlook.objects.filter(year=year, cost_position=36).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        rent_and_leasing = MOP_Outlook.objects.filter(year=year, cost_position=37).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        sold_fixed_assets = MOP_Outlook.objects.filter(year=year, cost_position=38).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        foreign_exchange_losses = MOP_Outlook.objects.filter(year=year, cost_position=39).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        training = MOP_Outlook.objects.filter(year=year, cost_position=40).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        provision_for_general_risks = MOP_Outlook.objects.filter(year=year, cost_position=41).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        insurance = MOP_Outlook.objects.filter(year=year, cost_position=42).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        other_group_charges = MOP_Outlook.objects.filter(year=year, cost_position=49).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        management_fees = MOP_Outlook.objects.filter(year=year, cost_position=43).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        other_expenses = MOP_Outlook.objects.filter(year=year, cost_position=44).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
        ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
        interests = MOP_Outlook.objects.filter(year=year, cost_position=46).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
        ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
        income_tax = MOP_Outlook.objects.filter(year=year, cost_position=50).aggregate(actual_value=Sum(f'flexed_outlook_{month}'))['actual_value'] or 0
        profit_after_tax = ebit + income_tax + interests
        profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

        Budget_Outlook_Flexed.objects.update_or_create(month=month, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    return HttpResponse("Budget_Outlook_Flexed_recalc OK")


def Outlook_Actual_recalc(request=None, month=None, year=None):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
    else:
        if not year:
            year = 2021
        
    if not month:
        for i in range(1,13):
            own_production = Ke5z_updated.filter(posting_period=i, fiscal_year=year, cost_position=1).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            merchandise = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=2).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            other_sales = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=48).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            sales_discounts = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=3).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            net_sales = own_production + merchandise + other_sales + sales_discounts
            work_in_progress = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=4).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            other_operating_income = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=5).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            revenues_total = net_sales + work_in_progress + other_operating_income
            foreign_exchange_gains = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=7).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            sundry_operating_income_expense = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=8).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
            ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
            material_direct = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=10).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
            oils_and_lubricants = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=11).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            energy_costs = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=12).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            tools = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=13).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            spare_parts = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=14).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            packaging = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=15).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            other_overhead_material = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=16).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            storage_fees_and_freight_in = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=17).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
            oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
            cost_of_goods_sold = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=19).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
            discounts_from_suppliers = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=20).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
            material_vs_total_revenues = material / revenues_total if revenues_total else 0
            direct_wages = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=22).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            personal_costs_indirect_salaried = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=23).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            personal_costs = direct_wages + personal_costs_indirect_salaried
            personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
            depreciation = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=25).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
            repairs_and_maintenance = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=26).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            provision_for_repairs_and_maintenance = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=27).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            freight_out = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=28).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            telecommunication_fees = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=29).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            warranty_claims = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=30).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            advisory_services = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=31).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            advertising = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=32).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            other_external_services = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=33).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            travel_expense = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=34).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            low_value_assets = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=35).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            taxes_and_fees = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=36).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            rent_and_leasing = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=37).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            sold_fixed_assets = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=38).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            foreign_exchange_losses = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=39).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            training = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=40).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            provision_for_general_risks = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=41).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            insurance = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=42).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            other_group_charges = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=49).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            management_fees = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=43).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            other_expenses = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=44).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
            ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
            interests = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=46).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
            ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
            income_tax = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=50).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            profit_after_tax = ebit + income_tax + interests
            profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

            Outlook_Actual.objects.update_or_create(month=i, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    else:
        own_production = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=1).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        merchandise = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=2).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        other_sales = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=48).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        sales_discounts = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=3).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        net_sales = own_production + merchandise + other_sales + sales_discounts
        work_in_progress = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=4).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        other_operating_income = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=5).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        revenues_total = net_sales + work_in_progress + other_operating_income
        foreign_exchange_gains = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=7).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        sundry_operating_income_expense = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=8).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
        ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
        material_direct = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=10).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
        oils_and_lubricants = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=11).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        energy_costs = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=12).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        tools = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=13).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        spare_parts = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=14).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        packaging = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=15).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        other_overhead_material = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=16).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        storage_fees_and_freight_in = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=17).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
        oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
        cost_of_goods_sold = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=19).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
        discounts_from_suppliers = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=20).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
        material_vs_total_revenues = material / revenues_total if revenues_total else 0
        direct_wages = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=22).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        personal_costs_indirect_salaried = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=23).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        personal_costs = direct_wages + personal_costs_indirect_salaried
        personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
        depreciation = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=25).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
        repairs_and_maintenance = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=26).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        provision_for_repairs_and_maintenance = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=27).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        freight_out = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=28).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        telecommunication_fees = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=29).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        warranty_claims = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=30).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        advisory_services = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=31).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        advertising = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=32).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        other_external_services = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=33).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        travel_expense = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=34).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        low_value_assets = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=35).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        taxes_and_fees = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=36).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        rent_and_leasing = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=37).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        sold_fixed_assets = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=38).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        foreign_exchange_losses = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=39).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        training = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=40).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        provision_for_general_risks = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=41).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        insurance = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=42).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        other_group_charges = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=49).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        management_fees = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=43).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        other_expenses = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=44).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
        ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
        interests = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=46).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
        ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
        income_tax = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=50).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        profit_after_tax = ebit + income_tax + interests
        profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

        Outlook_Actual.objects.update_or_create(month=month, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    return None


def Outlook_Outlook_recalc(request=None, month=None, year=None, version=4):
    
    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
        version = request.GET.get('version', 4)
    else:
        if not year:
            year = 2021
    
    if not month:
        for i in range(1,13):
            own_production = MOP_Outlook.objects.filter(year=year, cost_position=1).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            merchandise = MOP_Outlook.objects.filter(year=year, cost_position=2).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            other_sales = MOP_Outlook.objects.filter(year=year, cost_position=48).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            sales_discounts = MOP_Outlook.objects.filter(year=year, cost_position=3).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            net_sales = own_production + merchandise + other_sales + sales_discounts
            work_in_progress = MOP_Outlook.objects.filter(year=year, cost_position=4).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            other_operating_income = MOP_Outlook.objects.filter(year=year, cost_position=5).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            revenues_total = net_sales + work_in_progress + other_operating_income
            foreign_exchange_gains = MOP_Outlook.objects.filter(year=year, cost_position=7).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            sundry_operating_income_expense = MOP_Outlook.objects.filter(year=year, cost_position=8).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
            ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
            material_direct = MOP_Outlook.objects.filter(year=year, cost_position=10).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
            oils_and_lubricants = MOP_Outlook.objects.filter(year=year, cost_position=11).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            energy_costs = MOP_Outlook.objects.filter(year=year, cost_position=12).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            tools = MOP_Outlook.objects.filter(year=year, cost_position=13).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            spare_parts = MOP_Outlook.objects.filter(year=year, cost_position=14).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            packaging = MOP_Outlook.objects.filter(year=year, cost_position=15).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            other_overhead_material = MOP_Outlook.objects.filter(year=year, cost_position=16).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            storage_fees_and_freight_in = MOP_Outlook.objects.filter(year=year, cost_position=17).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
            oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
            cost_of_goods_sold = MOP_Outlook.objects.filter(year=year, cost_position=19).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
            discounts_from_suppliers = MOP_Outlook.objects.filter(year=year, cost_position=20).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
            material_vs_total_revenues = material / revenues_total if revenues_total else 0
            direct_wages = MOP_Outlook.objects.filter(year=year, cost_position=22).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            personal_costs_indirect_salaried = MOP_Outlook.objects.filter(year=year, cost_position=23).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            personal_costs = direct_wages + personal_costs_indirect_salaried
            personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
            depreciation = MOP_Outlook.objects.filter(year=year, cost_position=25).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
            repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=26).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            provision_for_repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=27).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            freight_out = MOP_Outlook.objects.filter(year=year, cost_position=28).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            telecommunication_fees = MOP_Outlook.objects.filter(year=year, cost_position=29).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            warranty_claims = MOP_Outlook.objects.filter(year=year, cost_position=30).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            advisory_services = MOP_Outlook.objects.filter(year=year, cost_position=31).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            advertising = MOP_Outlook.objects.filter(year=year, cost_position=32).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            other_external_services = MOP_Outlook.objects.filter(year=year, cost_position=33).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            travel_expense = MOP_Outlook.objects.filter(year=year, cost_position=34).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            low_value_assets = MOP_Outlook.objects.filter(year=year, cost_position=35).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            taxes_and_fees = MOP_Outlook.objects.filter(year=year, cost_position=36).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            rent_and_leasing = MOP_Outlook.objects.filter(year=year, cost_position=37).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            sold_fixed_assets = MOP_Outlook.objects.filter(year=year, cost_position=38).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            foreign_exchange_losses = MOP_Outlook.objects.filter(year=year, cost_position=39).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            training = MOP_Outlook.objects.filter(year=year, cost_position=40).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            provision_for_general_risks = MOP_Outlook.objects.filter(year=year, cost_position=41).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            insurance = MOP_Outlook.objects.filter(year=year, cost_position=42).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            other_group_charges = MOP_Outlook.objects.filter(year=year, cost_position=49).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            management_fees = MOP_Outlook.objects.filter(year=year, cost_position=43).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            other_expenses = MOP_Outlook.objects.filter(year=year, cost_position=44).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
            ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
            interests = MOP_Outlook.objects.filter(year=year, cost_position=46).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
            ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
            income_tax = MOP_Outlook.objects.filter(year=year, cost_position=50).aggregate(actual_sum=Sum(f'outlook_{i}_v{version}'))['actual_sum'] or 0
            profit_after_tax = ebit + income_tax + interests
            profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

            Outlook_Outlook.objects.update_or_create(version=version, month=i, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    else:
        own_production = MOP_Outlook.objects.filter(year=year, cost_position=1).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        merchandise = MOP_Outlook.objects.filter(year=year, cost_position=2).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        other_sales = MOP_Outlook.objects.filter(year=year, cost_position=48).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        sales_discounts = MOP_Outlook.objects.filter(year=year, cost_position=3).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        net_sales = own_production + merchandise + other_sales + sales_discounts
        work_in_progress = MOP_Outlook.objects.filter(year=year, cost_position=4).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        other_operating_income = MOP_Outlook.objects.filter(year=year, cost_position=5).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        revenues_total = net_sales + work_in_progress + other_operating_income
        foreign_exchange_gains = MOP_Outlook.objects.filter(year=year, cost_position=7).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        sundry_operating_income_expense = MOP_Outlook.objects.filter(year=year, cost_position=8).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
        ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
        material_direct = MOP_Outlook.objects.filter(year=year, cost_position=10).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
        oils_and_lubricants = MOP_Outlook.objects.filter(year=year, cost_position=11).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        energy_costs = MOP_Outlook.objects.filter(year=year, cost_position=12).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        tools = MOP_Outlook.objects.filter(year=year, cost_position=13).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        spare_parts = MOP_Outlook.objects.filter(year=year, cost_position=14).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        packaging = MOP_Outlook.objects.filter(year=year, cost_position=15).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        other_overhead_material = MOP_Outlook.objects.filter(year=year, cost_position=16).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        storage_fees_and_freight_in = MOP_Outlook.objects.filter(year=year, cost_position=17).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
        oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
        cost_of_goods_sold = MOP_Outlook.objects.filter(year=year, cost_position=19).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
        discounts_from_suppliers = MOP_Outlook.objects.filter(year=year, cost_position=20).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
        material_vs_total_revenues = material / revenues_total if revenues_total else 0
        direct_wages = MOP_Outlook.objects.filter(year=year, cost_position=22).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        personal_costs_indirect_salaried = MOP_Outlook.objects.filter(year=year, cost_position=23).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        personal_costs = direct_wages + personal_costs_indirect_salaried
        personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
        depreciation = MOP_Outlook.objects.filter(year=year, cost_position=25).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
        repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=26).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        provision_for_repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=27).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        freight_out = MOP_Outlook.objects.filter(year=year, cost_position=28).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        telecommunication_fees = MOP_Outlook.objects.filter(year=year, cost_position=29).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        warranty_claims = MOP_Outlook.objects.filter(year=year, cost_position=30).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        advisory_services = MOP_Outlook.objects.filter(year=year, cost_position=31).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        advertising = MOP_Outlook.objects.filter(year=year, cost_position=32).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        other_external_services = MOP_Outlook.objects.filter(year=year, cost_position=33).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        travel_expense = MOP_Outlook.objects.filter(year=year, cost_position=34).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        low_value_assets = MOP_Outlook.objects.filter(year=year, cost_position=35).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        taxes_and_fees = MOP_Outlook.objects.filter(year=year, cost_position=36).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        rent_and_leasing = MOP_Outlook.objects.filter(year=year, cost_position=37).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        sold_fixed_assets = MOP_Outlook.objects.filter(year=year, cost_position=38).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        foreign_exchange_losses = MOP_Outlook.objects.filter(year=year, cost_position=39).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        training = MOP_Outlook.objects.filter(year=year, cost_position=40).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        provision_for_general_risks = MOP_Outlook.objects.filter(year=year, cost_position=41).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        insurance = MOP_Outlook.objects.filter(year=year, cost_position=42).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        other_group_charges = MOP_Outlook.objects.filter(year=year, cost_position=49).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        management_fees = MOP_Outlook.objects.filter(year=year, cost_position=43).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        other_expenses = MOP_Outlook.objects.filter(year=year, cost_position=44).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
        ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
        interests = MOP_Outlook.objects.filter(year=year, cost_position=46).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
        ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
        income_tax = MOP_Outlook.objects.filter(year=year, cost_position=50).aggregate(actual_sum=Sum(f'outlook_{month}_v{version}'))['actual_sum'] or 0
        profit_after_tax = ebit + income_tax + interests
        profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

        Outlook_Outlook.objects.update_or_create(version=version, month=month, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    return None


def Outlook_Budget_recalc(request=None, month=None, year=None):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
    else:
        if not year:
            year = 2021
    
    if not month:
        for i in range(1,13):
            own_production = MOP_Outlook.objects.filter(year=year, cost_position=1).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            merchandise = MOP_Outlook.objects.filter(year=year, cost_position=2).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            other_sales = MOP_Outlook.objects.filter(year=year, cost_position=48).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            sales_discounts = MOP_Outlook.objects.filter(year=year, cost_position=3).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            net_sales = own_production + merchandise + other_sales + sales_discounts
            work_in_progress = MOP_Outlook.objects.filter(year=year, cost_position=4).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            other_operating_income = MOP_Outlook.objects.filter(year=year, cost_position=5).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            revenues_total = net_sales + work_in_progress + other_operating_income
            foreign_exchange_gains = MOP_Outlook.objects.filter(year=year, cost_position=7).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            sundry_operating_income_expense = MOP_Outlook.objects.filter(year=year, cost_position=8).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
            ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
            material_direct = MOP_Outlook.objects.filter(year=year, cost_position=10).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
            oils_and_lubricants = MOP_Outlook.objects.filter(year=year, cost_position=11).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            energy_costs = MOP_Outlook.objects.filter(year=year, cost_position=12).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            tools = MOP_Outlook.objects.filter(year=year, cost_position=13).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            spare_parts = MOP_Outlook.objects.filter(year=year, cost_position=14).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            packaging = MOP_Outlook.objects.filter(year=year, cost_position=15).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            other_overhead_material = MOP_Outlook.objects.filter(year=year, cost_position=16).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            storage_fees_and_freight_in = MOP_Outlook.objects.filter(year=year, cost_position=17).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
            oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
            cost_of_goods_sold = MOP_Outlook.objects.filter(year=year, cost_position=19).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
            discounts_from_suppliers = MOP_Outlook.objects.filter(year=year, cost_position=20).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
            material_vs_total_revenues = material / revenues_total if revenues_total else 0
            direct_wages = MOP_Outlook.objects.filter(year=year, cost_position=22).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            personal_costs_indirect_salaried = MOP_Outlook.objects.filter(year=year, cost_position=23).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            personal_costs = direct_wages + personal_costs_indirect_salaried
            personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
            depreciation = MOP_Outlook.objects.filter(year=year, cost_position=25).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
            repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=26).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            provision_for_repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=27).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            freight_out = MOP_Outlook.objects.filter(year=year, cost_position=28).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            telecommunication_fees = MOP_Outlook.objects.filter(year=year, cost_position=29).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            warranty_claims = MOP_Outlook.objects.filter(year=year, cost_position=30).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            advisory_services = MOP_Outlook.objects.filter(year=year, cost_position=31).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            advertising = MOP_Outlook.objects.filter(year=year, cost_position=32).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            other_external_services = MOP_Outlook.objects.filter(year=year, cost_position=33).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            travel_expense = MOP_Outlook.objects.filter(year=year, cost_position=34).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            low_value_assets = MOP_Outlook.objects.filter(year=year, cost_position=35).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            taxes_and_fees = MOP_Outlook.objects.filter(year=year, cost_position=36).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            rent_and_leasing = MOP_Outlook.objects.filter(year=year, cost_position=37).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            sold_fixed_assets = MOP_Outlook.objects.filter(year=year, cost_position=38).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            foreign_exchange_losses = MOP_Outlook.objects.filter(year=year, cost_position=39).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            training = MOP_Outlook.objects.filter(year=year, cost_position=40).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            provision_for_general_risks = MOP_Outlook.objects.filter(year=year, cost_position=41).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            insurance = MOP_Outlook.objects.filter(year=year, cost_position=42).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            other_group_charges = MOP_Outlook.objects.filter(year=year, cost_position=49).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            management_fees = MOP_Outlook.objects.filter(year=year, cost_position=43).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            other_expenses = MOP_Outlook.objects.filter(year=year, cost_position=44).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
            ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
            interests = MOP_Outlook.objects.filter(year=year, cost_position=46).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
            ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
            income_tax = MOP_Outlook.objects.filter(year=year, cost_position=50).aggregate(actual_sum=Sum(f'month_{i}'))['actual_sum'] or 0
            profit_after_tax = ebit + income_tax + interests
            profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

            Outlook_Budget.objects.update_or_create(month=i, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    else:
        own_production = MOP_Outlook.objects.filter(year=year, cost_position=1).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        merchandise = MOP_Outlook.objects.filter(year=year, cost_position=2).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        other_sales = MOP_Outlook.objects.filter(year=year, cost_position=48).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        sales_discounts = MOP_Outlook.objects.filter(year=year, cost_position=3).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        net_sales = own_production + merchandise + other_sales + sales_discounts
        work_in_progress = MOP_Outlook.objects.filter(year=year, cost_position=4).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        other_operating_income = MOP_Outlook.objects.filter(year=year, cost_position=5).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        revenues_total = net_sales + work_in_progress + other_operating_income
        foreign_exchange_gains = MOP_Outlook.objects.filter(year=year, cost_position=7).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        sundry_operating_income_expense = MOP_Outlook.objects.filter(year=year, cost_position=8).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        other_operating_income_expense = foreign_exchange_gains + sundry_operating_income_expense
        ooi_vs_total_revenues = (other_operating_income_expense / revenues_total) if revenues_total else 0
        material_direct = MOP_Outlook.objects.filter(year=year, cost_position=10).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        material_direct_vs_own_production_sales = material_direct / (own_production + work_in_progress) if (own_production or work_in_progress) else 0
        oils_and_lubricants = MOP_Outlook.objects.filter(year=year, cost_position=11).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        energy_costs = MOP_Outlook.objects.filter(year=year, cost_position=12).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        tools = MOP_Outlook.objects.filter(year=year, cost_position=13).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        spare_parts = MOP_Outlook.objects.filter(year=year, cost_position=14).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        packaging = MOP_Outlook.objects.filter(year=year, cost_position=15).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        other_overhead_material = MOP_Outlook.objects.filter(year=year, cost_position=16).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        storage_fees_and_freight_in = MOP_Outlook.objects.filter(year=year, cost_position=17).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        overhead_material = oils_and_lubricants + energy_costs + tools + spare_parts + packaging + other_overhead_material + storage_fees_and_freight_in
        oh_material_vs_total_revenues = overhead_material / revenues_total if revenues_total else 0
        cost_of_goods_sold = MOP_Outlook.objects.filter(year=year, cost_position=19).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        cost_of_goods_sold_vs_total_revenues = cost_of_goods_sold / merchandise if merchandise else 0 
        discounts_from_suppliers = MOP_Outlook.objects.filter(year=year, cost_position=20).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        material = cost_of_goods_sold + overhead_material + material_direct + discounts_from_suppliers
        material_vs_total_revenues = material / revenues_total if revenues_total else 0
        direct_wages = MOP_Outlook.objects.filter(year=year, cost_position=22).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        personal_costs_indirect_salaried = MOP_Outlook.objects.filter(year=year, cost_position=23).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        personal_costs = direct_wages + personal_costs_indirect_salaried
        personal_costs_vs_total_revenues = personal_costs / revenues_total if revenues_total else 0
        depreciation = MOP_Outlook.objects.filter(year=year, cost_position=25).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        depreciation_vs_total_revenues = depreciation / revenues_total if revenues_total else 0
        repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=26).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        provision_for_repairs_and_maintenance = MOP_Outlook.objects.filter(year=year, cost_position=27).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        freight_out = MOP_Outlook.objects.filter(year=year, cost_position=28).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        telecommunication_fees = MOP_Outlook.objects.filter(year=year, cost_position=29).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        warranty_claims = MOP_Outlook.objects.filter(year=year, cost_position=30).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        advisory_services = MOP_Outlook.objects.filter(year=year, cost_position=31).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        advertising = MOP_Outlook.objects.filter(year=year, cost_position=32).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        other_external_services = MOP_Outlook.objects.filter(year=year, cost_position=33).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        travel_expense = MOP_Outlook.objects.filter(year=year, cost_position=34).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        low_value_assets = MOP_Outlook.objects.filter(year=year, cost_position=35).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        taxes_and_fees = MOP_Outlook.objects.filter(year=year, cost_position=36).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        rent_and_leasing = MOP_Outlook.objects.filter(year=year, cost_position=37).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        sold_fixed_assets = MOP_Outlook.objects.filter(year=year, cost_position=38).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        foreign_exchange_losses = MOP_Outlook.objects.filter(year=year, cost_position=39).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        training = MOP_Outlook.objects.filter(year=year, cost_position=40).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        provision_for_general_risks = MOP_Outlook.objects.filter(year=year, cost_position=41).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        insurance = MOP_Outlook.objects.filter(year=year, cost_position=42).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        other_group_charges = MOP_Outlook.objects.filter(year=year, cost_position=49).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        management_fees = MOP_Outlook.objects.filter(year=year, cost_position=43).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        other_expenses = MOP_Outlook.objects.filter(year=year, cost_position=44).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        other_operating_expenses = repairs_and_maintenance + provision_for_repairs_and_maintenance + freight_out + telecommunication_fees + warranty_claims + advisory_services + advertising + other_external_services + travel_expense + low_value_assets + taxes_and_fees + rent_and_leasing + sold_fixed_assets + foreign_exchange_losses + training + provision_for_general_risks + insurance + other_group_charges + management_fees + other_expenses
        ooh_vs_total_revenues = other_operating_expenses / revenues_total if revenues_total else 0
        interests = MOP_Outlook.objects.filter(year=year, cost_position=46).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        ebit = revenues_total + other_operating_income_expense + material + personal_costs + depreciation + other_operating_expenses
        ebit_vs_total_revenues = ebit / revenues_total if revenues_total else 0
        income_tax = MOP_Outlook.objects.filter(year=year, cost_position=50).aggregate(actual_sum=Sum(f'month_{month}'))['actual_sum'] or 0
        profit_after_tax = ebit + income_tax + interests
        profit_after_tax_vs_total_revenues = profit_after_tax / revenues_total if revenues_total else 0 

        Outlook_Budget.objects.update_or_create(month=month, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'work_in_progress': work_in_progress, 'other_operating_income': other_operating_income, 'revenues_total': revenues_total, 'foreign_exchange_gains': foreign_exchange_gains, 'sundry_operating_income_expense': sundry_operating_income_expense, 'other_operating_income_expense': other_operating_income_expense, 'ooi_vs_total_revenues': ooi_vs_total_revenues, 'material_direct': material_direct, 'material_direct_vs_own_production_sales': material_direct_vs_own_production_sales, 'oils_and_lubricants': oils_and_lubricants, 'energy_costs': energy_costs, 'tools': tools, 'spare_parts': spare_parts, 'packaging': packaging, 'other_overhead_material': other_overhead_material, 'storage_fees_and_freight_in': storage_fees_and_freight_in, 'overhead_material': overhead_material, 'oh_material_vs_total_revenues': oh_material_vs_total_revenues, 'cost_of_goods_sold': cost_of_goods_sold, 'cost_of_goods_sold_vs_total_revenues': cost_of_goods_sold_vs_total_revenues, 'discounts_from_suppliers': discounts_from_suppliers, 'material': material, 'material_vs_total_revenues': material_vs_total_revenues, 'direct_wages': direct_wages, 'personal_costs_indirect_salaried': personal_costs_indirect_salaried, 'personal_costs': personal_costs, 'personal_costs_vs_total_revenues': personal_costs_vs_total_revenues, 'depreciation': depreciation, 'depreciation_vs_total_revenues': depreciation_vs_total_revenues, 'repairs_and_maintenance': repairs_and_maintenance, 'provision_for_repairs_and_maintenance': provision_for_repairs_and_maintenance, 'freight_out': freight_out, 'telecommunication_fees': telecommunication_fees, 'warranty_claims': warranty_claims, 'advisory_services': advisory_services, 'advertising': advertising, 'other_external_services': other_external_services, 'travel_expense': travel_expense, 'low_value_assets': low_value_assets, 'taxes_and_fees': taxes_and_fees, 'rent_and_leasing': rent_and_leasing, 'sold_fixed_assets': sold_fixed_assets, 'foreign_exchange_losses': foreign_exchange_losses, 'training': training, 'provision_for_general_risks': provision_for_general_risks, 'insurance': insurance, 'other_group_charges': other_group_charges, 'management_fees': management_fees, 'other_expenses': other_expenses, 'other_operating_expenses': other_operating_expenses, 'ooh_vs_total_revenues': ooh_vs_total_revenues, 'interests': interests, 'ebit': ebit, 'ebit_vs_total_revenues': ebit_vs_total_revenues, 'income_tax': income_tax, 'profit_after_tax': profit_after_tax, 'profit_after_tax_vs_total_revenues': profit_after_tax_vs_total_revenues})

    return None


def MOP_outlook_months_recalc(request=None, month=None, year=None, version=4):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
        version = request.GET.get('version', 4)
    else:
        if not year:
            year = 2021

    mop_rows = MOP_Outlook.objects.all()

    cost_positions_counter = {}

    for mop_row in mop_rows:
        if not mop_row.cost_position in cost_positions_counter:
            cost_positions_counter[mop_row.cost_position] = 1
        else:
            cost_positions_counter[mop_row.cost_position] += 1
       
    if not month:
        for i in range(1, 13):
            exec(f'mop_monthly_{i} = Outlook_MOP_Monthly.objects.get(version={version}, month={i}, year={year}).volume_flex_outlook_vs_budget')
    else:
        exec(f'mop_monthly_{month} = Outlook_MOP_Monthly.objects.get(version={version}, month={month}, year={year}).volume_flex_outlook_vs_budget')

    
    if not month:
        for i in range(1,13):
            for mop_row in mop_rows:
                exec(f'mop_row.outlook_{i}_v{version} = mop_row.month_{i} - (mop_row.month_{i} * mop_row.flexibility_rate * mop_monthly_{i})')
                mop_row.save()
    else:
        for mop_row in mop_rows:
            exec(f'mop_row.outlook_{month}_v{version} = mop_row.month_{month} - (mop_row.month_{month} * mop_row.flexibility_rate * mop_monthly_{month})')
            mop_row.save()


    if month:
        outlook_corrections = Outlook_Corrections.objects.filter(year=year, month=month).values('year', 'month', 'cost_position').annotate(aggregated_amount=Sum("amount"))
    
        for correction in outlook_corrections:
            mop_rows_to_update = MOP_Outlook.objects.filter(cost_position=correction['cost_position'], year=correction['year'])
            for mop_row in mop_rows_to_update:
                exec(f'mop_row.outlook_{month}_v{version} = mop_row.month_{month} - (mop_row.month_{month} * mop_row.flexibility_rate * mop_monthly_{month}) + (correction["aggregated_amount"] / cost_positions_counter[mop_row.cost_position])')
                mop_row.save() 
    else:
        for i in range(1, 13):
            outlook_corrections = Outlook_Corrections.objects.filter(year=year, month=i).values('year', 'month', 'cost_position').annotate(aggregated_amount=Sum("amount"))
            for correction in outlook_corrections:
                mop_rows_to_update = MOP_Outlook.objects.filter(cost_position=correction['cost_position'], year=correction['year'])
                for mop_row in mop_rows_to_update:
                    exec(f'mop_row.outlook_{i}_v{version} = mop_row.month_{i} - (mop_row.month_{i} * mop_row.flexibility_rate * mop_monthly_{i}) + (correction["aggregated_amount"] / cost_positions_counter[mop_row.cost_position])')
                    mop_row.save()

    return HttpResponse("MOP Outlook Months calculcation done")


def MOP_flexed_months_recalc(request=None, month=None, year=None, version=4):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
        version = request.GET.get('version', 4)
    else:
        if not year:
            year = 2021

    mop_rows = MOP_Outlook.objects.all()

    if not month:
        for i in range(1, 13):
            exec(f'actual_sales_monthly_{i} = Outlook_Sales_Actual.objects.get(version={version}, month={i}, year={year}).volume_flex_actual_vs_outlook')
    else:
        exec(f'actual_sales_monthly_{month} = Outlook_Sales_Actual.objects.get(version={version}, month={month}, year={year}).volume_flex_actual_vs_outlook')

    for mop_row in mop_rows:
        if not month:
            for i in range(1,13):
                exec(f'mop_row.flexed_outlook_{i} = mop_row.outlook_{i}_v{version} + (mop_row.outlook_{i}_v{version} * mop_row.flexibility_rate * actual_sales_monthly_{i})')
                mop_row.save()
        else:
            exec(f'mop_row.flexed_outlook_{month} = mop_row.outlook_{month}_v{version} + (mop_row.outlook_{month}_v{version} * mop_row.flexibility_rate * actual_sales_monthly_{month})')
            mop_row.save()

    return None


def outlook_mop_monthly(request=None, month=None, year=None, version=4):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
        version = request.GET.get('version', 4)
    else:
        if not year:
            year = 2021

    if not month:
        for i in range(1,13):
            own_production = MOP_Outlook.objects.filter(year=year, cost_position=1).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            merchandise = MOP_Outlook.objects.filter(year=year, cost_position=2).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            other_sales = MOP_Outlook.objects.filter(year=year, cost_position=48).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            sales_discounts = MOP_Outlook.objects.filter(year=year, cost_position=3).aggregate(actual_value=Sum(f'month_{i}'))['actual_value'] or 0
            net_sales = own_production + merchandise + other_sales + sales_discounts
            outlook_sales_estimation_net_sales = Outlook_Sales_Estimation.objects.get(version=version, month=i, year=year).net_sales
            volume_flex_outlook_vs_budget = 1 - (outlook_sales_estimation_net_sales/-net_sales)

            Outlook_MOP_Monthly.objects.update_or_create(version=version, month=i, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'volume_flex_outlook_vs_budget': volume_flex_outlook_vs_budget})
    else:
        own_production = MOP_Outlook.objects.filter(year=year, cost_position=1).aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        merchandise = MOP_Outlook.objects.filter(year=year, cost_position=2).aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        other_sales = MOP_Outlook.objects.filter(year=year, cost_position=48).aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        sales_discounts = MOP_Outlook.objects.filter(year=year, cost_position=3).aggregate(actual_value=Sum(f'month_{month}'))['actual_value'] or 0
        net_sales = own_production + merchandise + other_sales + sales_discounts
        outlook_sales_estimation_net_sales = Outlook_Sales_Estimation.objects.get(version=version, month=month, year=year).net_sales
        volume_flex_outlook_vs_budget = 1 - (outlook_sales_estimation_net_sales/-net_sales)

        print(volume_flex_outlook_vs_budget)


        Outlook_MOP_Monthly.objects.update_or_create(version=version, month=month, year=year, defaults={'own_production': own_production, 'merchandise': merchandise, 'other_sales': other_sales, 'sales_discounts': sales_discounts, 'net_sales': net_sales, 'volume_flex_outlook_vs_budget': volume_flex_outlook_vs_budget})

    return None


def outlook_sales_actual(request=None, month=None, year=None, version=4):

    if request:
        year = request.GET.get('year', 2021)
        month = request.GET.get('month', None)
        version = request.GET.get('version', 4)
    else:
        if not year:
            year = 2021

    if not month:

        for i in range(1,13):
            gross_sales = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=1).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            merchandise_sales = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position=2).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            other_revenues = Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position__in=[3,48]).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
            net_sales = gross_sales + merchandise_sales + other_revenues
            outlook_sales_estimation = Outlook_Sales_Estimation.objects.get(version=version, month=i, year=year).net_sales
            volume_flex_actual_vs_outlook = -(1 - (-net_sales/outlook_sales_estimation)) if net_sales else 0
            print(volume_flex_actual_vs_outlook)
            Outlook_Sales_Actual.objects.update_or_create(version=version, month=i, year=year, defaults={'gross_sales': gross_sales, 'merchandise_sales': merchandise_sales, 'other_revenues': other_revenues, 'volume_flex_actual_vs_outlook': volume_flex_actual_vs_outlook, 'net_sales': net_sales})

    else:
        gross_sales = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=1).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        merchandise_sales = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position=2).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        other_revenues = Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position__in=[3,48]).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'] or 0
        net_sales = gross_sales + merchandise_sales + other_revenues
        outlook_sales_estimation = Outlook_Sales_Estimation.objects.get(version=version, month=month, year=year).net_sales
        volume_flex_actual_vs_outlook = -(1 - (-net_sales/outlook_sales_estimation)) if net_sales else 0
        print(volume_flex_actual_vs_outlook)
        Outlook_Sales_Actual.objects.update_or_create(version=version, month=month, year=year, defaults={'gross_sales': gross_sales, 'merchandise_sales': merchandise_sales, 'other_revenues': other_revenues, 'volume_flex_actual_vs_outlook': volume_flex_actual_vs_outlook, 'net_sales': net_sales})

    return None


def outlook_sales_estimation(request=None, month=None, year=None, version=4):

    if request:
        year = request.GET.get('year', 2021)
        version = request.GET.get('version', 4)
    else:
        if not year:
            year = 2021

    sales_from_munich = Sales_From_Munich.objects.filter(category=version)

    # gross_sales_coef = float(request.GET.get('gross_sales_coef', 0.922945851807476))
    gross_sales_coef = 0.922945851807476
    merchandise_sales_coef = 1 - gross_sales_coef
    fx_rate = 25850000

    if not month:
        for i in range(1,13):
            Outlook_Sales_Estimation.objects.update_or_create(version=version, month=i, year=year, defaults={'gross_sales': sales_from_munich.get(month=i, year=year).total_gross_sales * gross_sales_coef * fx_rate, 'merchandise_sales': sales_from_munich.get(month=i, year=year).total_gross_sales * merchandise_sales_coef * fx_rate, 'other_revenues': sales_from_munich.get(month=i, year=year).other_revenues * fx_rate, 'net_sales': (sales_from_munich.get(month=i, year=year).total_gross_sales * gross_sales_coef * fx_rate) + (sales_from_munich.get(month=i, year=year).total_gross_sales * merchandise_sales_coef * fx_rate) + (sales_from_munich.get(month=i, year=year).other_revenues * fx_rate) })
    else:
        Outlook_Sales_Estimation.objects.update_or_create(version=version, month=month, year=year, defaults={'gross_sales': sales_from_munich.get(month=month, year=year).total_gross_sales * gross_sales_coef * fx_rate, 'merchandise_sales': sales_from_munich.get(month=month, year=year).total_gross_sales * merchandise_sales_coef * fx_rate, 'other_revenues': sales_from_munich.get(month=month, year=year).other_revenues * fx_rate, 'net_sales': (sales_from_munich.get(month=month, year=year).total_gross_sales * gross_sales_coef * fx_rate) + (sales_from_munich.get(month=month, year=year).total_gross_sales * merchandise_sales_coef * fx_rate) + (sales_from_munich.get(month=month, year=year).other_revenues * fx_rate)})

    outlook_mop_monthly(None, month, year)
    outlook_sales_actual(None, month, year)

    return HttpResponse("Non-threaded operations successfull")


def outlook_calculate_all(request=None, month=None, year=None):

    if request:
        year = request.GET.get('year')
        month = request.GET.get('month')

    outlook_sales_actual(None, month, year)
    MOP_outlook_months_recalc(None, month, year)
    outlook_mop_monthly(None, month, year)
    Outlook_Actual_recalc(None, month, year)
    Outlook_Outlook_recalc(None, month, year)
    Outlook_Budget_recalc(None, month, year)

    return None


def salesbook_budget_calculation(request=None, month=None, year=None):

    if request:
        month = request.GET.get('month')
        year = request.GET.get('year')

    else:
        year = 2021

    list_of_cocs = list(MOP.objects.filter(cost_center__icontains='coc').values_list('profit_center', flat=True).exclude(profit_center__in=['COC12', 'COC14']).distinct('profit_center'))
    list_of_cocs.append('all')

    if not year:
        year = 2021

    if not month:
        for coc in list_of_cocs:
            for i in range(1, 13):
                if not coc == 'all':
                    Salesbook_Budget.objects.update_or_create(coc=coc, month=i, year=year, defaults={'budget_value':  -MOP.objects.filter(profit_center=coc, year=year, cost_position__in=[1,2,3,48]).aggregate(budget_value=Sum(f'month_{i}'))['budget_value']})
                else:
                    Salesbook_Budget.objects.update_or_create(coc=coc, month=i, year=year, defaults={'budget_value':  Salesbook_Budget.objects.filter(year=year, month=i).aggregate(budget_value=Sum(f'budget_value'))['budget_value']})
    else:
        for coc in list_of_cocs:
            if not coc == 'all':
                Salesbook_Budget.objects.update_or_create(coc=coc, month=month, year=year, defaults={'budget_value':  -MOP.objects.filter(profit_center=coc, year=year, cost_position__in=[1,2,3,48]).aggregate(budget_value=Sum(f'month_{month}'))['budget_value']})
            else:
                Salesbook_Budget.objects.update_or_create(coc=coc, month=i, year=year, defaults={'budget_value':  Salesbook_Budget.objects.filter(year=year, month=month).aggregate(budget_value=Sum(f'budget_value'))['budget_value']})

    return None


def salesbook_actual_calculation(request=None, month=None, year=None):

    if request:
        month = request.GET.get('month')
        year = request.GET.get('year')

    if not year:
        year = 2021

    list_of_cocs = list(MOP.objects.filter(cost_center__icontains='coc').values_list('profit_center', flat=True).exclude(profit_center__in=['COC12', 'COC14']).distinct('profit_center'))
    list_of_cocs_wo_coc_24 = list_of_cocs.copy()
    list_of_cocs_wo_coc_24.remove('COC24')


    if not month:
        for i in range(1,13):
            for coc in list_of_cocs_wo_coc_24:
                try:
                    Salesbook_Actual.objects.update_or_create(coc=coc, month=i, year=year, defaults={'actual_value': -1 * (Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, profit_center=coc, cost_position__in=[1,2,3,48], record_type=0).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'])})
                except:
                    Salesbook_Actual.objects.update_or_create(coc=coc, month=i, year=year, defaults={'actual_value': 0})
        
            try:
                Salesbook_Actual.objects.update_or_create(coc='COC24', month=i, year=year, defaults={'actual_value': -1 * (Ke5z_updated.objects.filter(posting_period=i, fiscal_year=year, cost_position__in=[1,2,3,48], record_type=0).exclude(profit_center__in=list_of_cocs_wo_coc_24).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'])})    
            except:
                Salesbook_Actual.objects.update_or_create(coc='COC24', month=i, year=year, defaults={'actual_value': 0})    

            try:
                Salesbook_Actual.objects.update_or_create(coc='all', month=i, year=year, defaults={'actual_value': Salesbook_Actual.objects.filter(month=i, year=year).exclude(coc='all').aggregate(actual_value=Sum('actual_value'))['actual_value']})
            except:
                Salesbook_Actual.objects.update_or_create(coc='all', month=i, year=year, defaults={'actual_value': 0})


    
    else:
        for coc in list_of_cocs_wo_coc_24:
            try:
                Salesbook_Actual.objects.update_or_create(coc=coc, month=month, year=year, defaults={'actual_value': -1 * (Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, profit_center=coc, cost_position__in=[1,2,3,48], record_type=0).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'])})
            except:
                Salesbook_Actual.objects.update_or_create(coc=coc, month=month, year=year, defaults={'actual_value': 0})


        try:
            Salesbook_Actual.objects.update_or_create(coc='COC24', month=month, year=year, defaults={'actual_value': -1 * (Ke5z_updated.objects.filter(posting_period=month, fiscal_year=year, cost_position__in=[1,2,3,48], record_type=0).exclude(profit_center__in=list_of_cocs_wo_coc_24).aggregate(actual_value=Sum('in_profit_center_local_currency'))['actual_value'])})  
        except:
            Salesbook_Actual.objects.update_or_create(coc='COC24', month=month, year=year, defaults={'actual_value': 0})  

        try:
            Salesbook_Actual.objects.update_or_create(coc='all', month=month, year=year, defaults={'actual_value': Salesbook_Actual.objects.filter(month=month, year=year).exclude(coc='all').aggregate(actual_value=Sum('actual_value'))['actual_value']})
        except:
            Salesbook_Actual.objects.update_or_create(coc='all', month=month, year=year, defaults={'actual_value': 0})


    return None


def salesbook_actual_budget_split_calculation(request=None, month=None, year=None):

    if request:
        month = request.GET.get('month')
        year = request.GET.get('year')

    if not year:
        year = 2021
    
    if month:
        salesbook_actual_objects = Salesbook_Actual.objects.filter(month=month, year=year)
        salesbook_budget_objects = Salesbook_Budget.objects.filter(month=month, year=year)
    
        for _ in salesbook_actual_objects:
            split_value = _.actual_value / salesbook_budget_objects.get(coc=_.coc).budget_value
            Salesbook_Actual_Budget_Split.objects.update_or_create(month=month, year=year, coc=_.coc, defaults={'percentage': (1 - split_value) if not (1 - split_value) == 1 else 1})
    
    else:
        for i in range(1,13):
            salesbook_actual_objects = Salesbook_Actual.objects.filter(month=i, year=year)
            salesbook_budget_objects = Salesbook_Budget.objects.filter(month=i, year=year)
    
            for _ in salesbook_actual_objects:
                split_value = _.actual_value / salesbook_budget_objects.get(coc=_.coc).budget_value
                Salesbook_Actual_Budget_Split.objects.update_or_create(month=i, year=year, coc=_.coc, defaults={'percentage': (1 - split_value) if not (1 - split_value) == 1 else 0})

    return None


def mop_flexed_budget_month_calculation(request=None, month=None, year=None):

    if request:
        month = request.GET.get('month')
        year = request.GET.get('year')

    if not year:
        year = 2021

    context = {}

    mop_objects = MOP.objects.all()

    flexed_month_attribute = f'flexed_budget_month_{month}'
    budget_month_attribute = f'month_{month}'

    for _ in mop_objects:
        budget_month_value = getattr(_, budget_month_attribute)
        coc_allocation_percentage = round(Salesbook_Actual_Budget_Split.objects.get(coc=_.coc_allocation_key, month=month, year=year).percentage, 4)
        flexed_month_value = round(budget_month_value - (budget_month_value * round(_.flexibility_rate, 4) * coc_allocation_percentage), 2)
        setattr(_, flexed_month_attribute, flexed_month_value)
        _.save()

    Budget_Flexed_Budget_recalc(None, month, year)

    return HttpResponse("mop_flexed_budget_month_calculcation OK")


def mm1_to_dict():

    mm1_dict = {}
    mm1_data = MM1.objects.all()

    for data_row in mm1_data:
        mm1_dict[data_row.account] = [data_row.row_index, data_row.row_name]

    return mm1_dict


def mm2_to_dict():

    mm2_dict = {}
    mm2_data = MM2.objects.all()

    for data_row in mm2_data:
        mm2_dict[data_row.cost_center] = [data_row.first_level_mgr, data_row.second_level_mgr]

    return mm2_dict


def mm4_to_dict():

    mm4_dict = {}
    mm4_data = MM4.objects.all()

    for data_row in mm4_data:
        mm4_dict[data_row.ind_account] = [data_row.status, data_row.responsibility_group]

    return mm4_dict


def mm5_to_dict():

    mm5_dict = {}
    mm5_data = MM5.objects.all()

    for data_row in mm5_data:
        mm5_dict[data_row.functional_area] = [data_row.second_level, data_row.poc_gen_costs]

    return mm5_dict


def mm6_to_dict():

    mm6_dict = {}
    mm6_data = MM6.objects.all()

    for data_row in mm6_data:
        mm6_dict[data_row.fa_first_level] = data_row.description

    return mm6_dict


def mm7_to_dict():

    mm7_dict = {}
    mm7_data = MM7.objects.all()

    for data_row in mm7_data:
        mm7_dict[data_row.account_number] = [data_row.text_fir_bs_pl_item_3, data_row.group_account_number]

    return mm7_dict


def flexrates_to_dict():

    flex_dict = {}
    flex_data = Flexrates.objects.all()

    for data_row in flex_data:
        flex_dict[(data_row.group_account, data_row.functional_area)] = data_row.flexibility

    return flex_dict


def ksb1(request):

    ksb1_data = Ksb1.objects.all()

    context = {
        'ksb1_data': ksb1_data,
    }

    return render(request, "ksb1.html", context)


def ksb1_to_dict(reman=False):

    ksb1_dict = {}
    if not reman:
        ksb1_data = Ksb1.objects.all()

        for data_row in ksb1_data:
            if data_row.ref_document_number:
                ksb1_dict[(data_row.ref_document_number, data_row.posting_row_1, data_row.time_period)] = [data_row.name_of_offsetting_account, data_row.document_header_text]
            else:
                ksb1_dict[('', data_row.posting_row_1, data_row.time_period)] = [data_row.name_of_offsetting_account, data_row.document_header_text]
    else:
        ksb1_data = Ksb1_reman.objects.all()

        for data_row in ksb1_data:
            if data_row.ref_document_number:
                ksb1_dict[(data_row.ref_document_number, data_row.posting_row_1, data_row.time_period)] = [data_row.name_of_offsetting_account, data_row.document_header_text]
            else:
                ksb1_dict[('', data_row.posting_row_1, data_row.time_period)] = [data_row.name_of_offsetting_account, data_row.document_header_text]

    return ksb1_dict


def ke5z(request, period=False, year=False, reman=False):

    sendmail(None, f"Start toho {reman} celyho", "Start")

    mm1_dict = mm1_to_dict()
    mm2_dict = mm2_to_dict()
    mm4_dict = mm4_to_dict()
    mm5_dict = mm5_to_dict()
    mm6_dict = mm6_to_dict()
    mm7_dict = mm7_to_dict()
    flex_dict = flexrates_to_dict()
    ksb1_dict = ksb1_to_dict(reman=reman)

    period = request.GET.get('period')
    year = request.GET.get('year')

    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM controlling_ke5z_updated WHERE fiscal_year = {year} AND posting_period = {period}")

    ke5z_data = list(Ke5z.objects.filter(posting_period=period, fiscal_year=year))
    # Ke5z_updated_temp.objects.all().delete()

    for item in ke5z_data:
        row_data = {}
        row_data['transaction_description'] = ksb1_dict.get((str(item.reference_document), item.document_line, item.posting_period), ['',''])[1] if item.reference_document else ksb1_dict.get(('', item.document_line, item.posting_period), ['',''])[1]
        row_data['transaction_description'] = row_data['transaction_description'] if not row_data['transaction_description'] == '' else item.account_text 
        row_data['supplier'] = ksb1_dict.get((str(item.reference_document), item.document_line, item.posting_period), ['',''])[0]
        row_data['supplier'] = row_data['supplier'] if not row_data['supplier'] == "Utilities      P.ACC" else item.text
        row_data['posting_period'] = item.posting_period
        row_data['fiscal_year'] = item.fiscal_year
        row_data['text'] = item.text
        row_data['in_profit_center_local_currency'] = item.in_profit_center_local_currency
        row_data['profit_center_local_currency'] = item.profit_center_local_currency
        row_data['cost_center'] = item.profit_center if item.profit_center.startswith('COC') else (item.profit_center[3:] if not item.profit_center == "DUMMY" else "DUMMY")
        row_data['profit_center'] = item.profit_center
        row_data['account_number'] = item.account_number
        row_data['account_text'] = item.account_text
        row_data['purchasing_document'] = item.purchasing_document
        row_data['order_number'] = item.order_number
        row_data['quantity'] = item.quantity
        row_data['document_type_1'] = item.document_type_1
        row_data['partner_profit_center'] = item.partner_profit_center
        row_data['functional_area'] = item.functional_area
        row_data['document_type_2'] = item.document_type_2
        row_data['document_category'] = item.document_category
        row_data['document_number'] = item.document_number
        row_data['material'] = item.material
        row_data['document_type_3'] = item.document_type_3
        row_data['posting_date'] = item.posting_date
        row_data['trading_partner'] = item.trading_partner
        row_data['reference_document'] = item.reference_document
        row_data['reference_document_line'] = item.reference_document_line
        row_data['document_line'] = item.document_line
        row_data['username'] = item.username
        row_data['purchasing_document_item'] = item.purchasing_document_item
        row_data['record_type'] = item.record_type
        # row_data['pulled_on'] = item.pulled_on
        row_data['cost_position'], row_data['cost_position_text'] = mm1_dict[item.account_number] if item.account_number in mm1_dict else ('0', 'Chybí data')
        row_data['affectability'], row_data['responsibility_group'] = mm4_dict[item.account_number] if item.account_number in mm4_dict else ['Ovlivnitelné', 'Direct']
        row_data['first_line_manager'], row_data['second_line_manager'] =  mm2_dict[row_data['cost_center']] if row_data['cost_center'] in mm2_dict else ["Chybí data", "Chybí data"]
        row_data['fa_description'], row_data['poc_gc'] = mm5_dict[item.functional_area] if item.functional_area in mm5_dict else ('Chybí data', 'Chybí data')
        row_data['fa_group'] = item.functional_area[0:2] if item.functional_area else "Chybí data"
        row_data['fa_group_name'] = mm6_dict[row_data['fa_group']] if row_data['fa_group'] in mm6_dict else "Chybí zdrojová data"
        row_data['cz_account_name'], row_data['group_account'] = mm7_dict[item.account_number] if item.account_number in mm7_dict else ('Chybí data', 'Chybí data')
        row_data['flexibility_rate'] = flex_dict[(row_data['group_account'], item.functional_area)] if (row_data['group_account'], item.functional_area) in flex_dict else 0

        Ke5z_updated.objects.create(**row_data)
    
    # with connection.cursor() as cursor:
    #     cursor.execute(f"DELETE FROM controlling_ke5z_updated WHERE fiscal_year = {year} AND posting_period = {period}")
    #     cursor.execute(f"INSERT INTO controlling_ke5z_updated(posting_period, fiscal_year, text, in_profit_center_local_currency, profit_center_local_currency, cost_center, profit_center, account_number, account_text, purchasing_document, order_number, quantity, document_type_1, partner_profit_center, functional_area, document_type_2, document_category, document_number, material, document_type_3, posting_date, trading_partner, reference_document, reference_document_line, document_line, username, purchasing_document_item, pulled_on, cost_position, cost_position_text, affectability, responsibility_group, first_line_manager, second_line_manager, fa_description, fa_group, fa_group_name, poc_gc, cz_account_name, group_account, flexibility_rate, transaction_description, supplier, record_type) SELECT posting_period, fiscal_year, text, in_profit_center_local_currency, profit_center_local_currency, cost_center, profit_center, account_number, account_text, purchasing_document, order_number, quantity, document_type_1, partner_profit_center, functional_area, document_type_2, document_category, document_number, material, document_type_3, posting_date, trading_partner, reference_document, reference_document_line, document_line, username, purchasing_document_item, pulled_on, cost_position, cost_position_text, affectability, responsibility_group, first_line_manager, second_line_manager, fa_description, fa_group, fa_group_name, poc_gc, cz_account_name, group_account, flexibility_rate, transaction_description, supplier, record_type FROM controlling_ke5z_updated_temp")

    if str(period[0]) == "0":
        period = period[1]

    print("ke5z finish")

    # outlook_sales_actual(None, period, year)
    # salesbook_actual_calculation(None, period, year)
    # salesbook_actual_budget_split_calculation(None, period, year)
    # Outlook_Actual_recalc(None, period, year)
    # Actual_Costbook_recalc(None, period, year)
    # mop_flexed_budget_month_calculation(None, period, year)
    # Budget_Outlook_Flexed_recalc(None, period, year)
    # Budget_Flexed_Costbook_recalc(None, period, year)
    # Budget_Costbook_recalc(None, period, year)
    # # prepare_manager_report(None, period, year)
    # outlook_mop_monthly(None, period, year)
    # MOP_outlook_months_recalc(None, period, year)
    # MOP_flexed_months_recalc(None, period, year)
    # Outlook_Outlook_recalc(None, period, year)


    sendmail(None, "Konec toho celyho", "Konec")

    return HttpResponse("OK")


def get_manager(username):

    return Manager.objects.get(name=username)


def authenticate(login, password):

    SPECIAL_USERS = {'Pesnicak, Jan': 'nove_heslo', 'Pejsarova, Katerina': 'nove_heslo', 'Vajda, Peter': 'nove_heslo'}

    if not login in SPECIAL_USERS:
        try:
            ldap_username = f'{login.split(", ")[1]}.{login.split(", ")[0]}@knorr-bremse.com'
        except:
            ldap_username = f'{login.split(" ")[1]}.{login.split(" ")[0]}@knorr-bremse.com'
        ldap_password = password
    else:
        if SPECIAL_USERS[login] == password:
            return True
        else:
            return False

    print(ldap_password)

    connect = ldap.initialize("ldap://corp.knorr-bremse.com")
    connect.set_option(ldap.OPT_REFERRALS, 0)
    connect.simple_bind_s(ldap_username, ldap_password)
    result = connect.search_s("DC=corp,DC=knorr-bremse,DC=com", ldap.SCOPE_SUBTREE, 'userPrincipalName=' + ldap_username, ['userprincipalname', 'uid', 'samaccountname', 'mailnickname'])

    if result[0][1]['userPrincipalName'][0].decode('utf-8') == ldap_username:
        return True
    else:
        return False


def prepare_manager_report(request=None, last_month=None, year=None):

    if request:
        last_month = request.GET.get('last_month')
        year = request.GET.get('year')

    months_range = list(range(1, int(last_month) + 1))
    posting_periods = str(set(months_range))
    posting_periods = '(' + posting_periods[1:-1] + ')'

    flexed_budget_months = str([f'SUM(flexed_budget_month_{i}) flexed_budget_{i}' for i in months_range])
    flexed_budget_months = flexed_budget_months[1:-1]
    flexed_budget_months = flexed_budget_months.replace("'", "")
    mop_flexed_budget_months = str([f'flexed_budget_{i}' for i in months_range])
    mop_flexed_budget_months = mop_flexed_budget_months[1:-1]
    mop_flexed_budget_months = mop_flexed_budget_months.replace("'", "")
    mop_flexed_budget_per_line = str([f'ROUND(COALESCE(mop.flexed_budget_{i} / counts.t_count, 0)::numeric, 2) AS flexed_budget_m_{i}' for i in months_range])
    mop_flexed_budget_per_line = mop_flexed_budget_per_line[1:-1]
    mop_flexed_budget_per_line = mop_flexed_budget_per_line.replace("'", "")
    flexed_budget_months_for_union = str([f'ROUND(not_used_mop_keys_with_values.flexed_budget_{i}::numeric, 2)' for i in months_range])
    flexed_budget_months_for_union = flexed_budget_months_for_union[1:-1]
    flexed_budget_months_for_union = flexed_budget_months_for_union.replace("'", "")

    custom_query = f"WITH mop AS (SELECT {flexed_budget_months}, controlling_mm2.first_level_mgr AS first_line_manager, controlling_mm2.second_level_mgr AS second_line_manager, poc_gc, controlling_mop.cost_position, affectability, controlling_mop.cost_center, profit_center, local_account, functional_area, trading_partner FROM controlling_mop LEFT JOIN controlling_mm2 ON controlling_mm2.cost_center = controlling_mop.cost_center WHERE year = {year} GROUP BY controlling_mm2.first_level_mgr, controlling_mm2.second_level_mgr, account_description_cs, poc_gc, cost_position, affectability, profit_center, local_account, functional_area, trading_partner, controlling_mop.cost_center), mm_cost_position AS (SELECT DISTINCT row_index, row_name, account, account_name FROM controlling_mm1), counts AS (SELECT COUNT(id) t_count, profit_center, account_number, functional_area, trading_partner, fiscal_year FROM controlling_ke5z_updated WHERE fiscal_year = {year} AND posting_period IN {posting_periods} AND record_type = 0 GROUP BY profit_center, account_number, functional_area, trading_partner, fiscal_year), keys_in_actual AS (SELECT DISTINCT cost_center, profit_center, account_number, functional_area, trading_partner FROM controlling_ke5z_updated WHERE record_type = 0 AND fiscal_year = {year} AND posting_period IN {posting_periods} GROUP BY profit_center, account_number, functional_area, trading_partner, cost_center), keys_in_mop AS (SELECT DISTINCT cost_center, profit_center, local_account::integer, functional_area, trading_partner FROM controlling_mop WHERE year = {year}), not_used_mop_keys AS (SELECT * FROM keys_in_mop EXCEPT (SELECT * FROM keys_in_actual)), not_used_mop_keys_with_values AS (SELECT not_used_mop_keys.profit_center, not_used_mop_keys.local_account::integer, not_used_mop_keys.functional_area, not_used_mop_keys.trading_partner, {mop_flexed_budget_months}, mop.cost_center, controlling_mm2.first_level_mgr, controlling_mm2.second_level_mgr, mop.poc_gc, mop.cost_position, mop.affectability FROM not_used_mop_keys LEFT JOIN mop ON mop.profit_center = not_used_mop_keys.profit_center AND mop.cost_center = not_used_mop_keys.cost_center AND mop.local_account::integer = not_used_mop_keys.local_account AND mop.functional_area = not_used_mop_keys.functional_area AND mop.trading_partner = not_used_mop_keys.trading_partner LEFT JOIN controlling_mm2 ON not_used_mop_keys.cost_center = controlling_mm2.cost_center) SELECT controlling_ke5z_updated.posting_period, controlling_ke5z_updated.fiscal_year, text, ROUND(in_profit_center_local_currency::numeric, 2) AS in_profit_center_local_currency, controlling_ke5z_updated.cost_center, controlling_ke5z_updated.profit_center, controlling_ke5z_updated.account_number, controlling_ke5z_updated.cz_account_name AS account_name, purchasing_document, quantity,controlling_ke5z_updated.functional_area, document_number, material, posting_date, controlling_ke5z_updated.trading_partner, controlling_ke5z_updated.reference_document, reference_document_line, document_line, username, purchasing_document_item, controlling_ke5z_updated.cost_position, cost_position_text, controlling_ke5z_updated.affectability, responsibility_group, controlling_ke5z_updated.first_line_manager, controlling_ke5z_updated.second_line_manager, fa_description, fa_group_name, controlling_ke5z_updated.poc_gc, cz_account_name, group_account, flexibility_rate, transaction_description, supplier, (COALESCE(controlling_accruals.accruals_qualifier, False)) AS accruals, {mop_flexed_budget_per_line} FROM controlling_ke5z_updated LEFT JOIN mop ON controlling_ke5z_updated.profit_center = mop.profit_center AND controlling_ke5z_updated.account_number = mop.local_account::integer AND controlling_ke5z_updated.functional_area = mop.functional_area AND controlling_ke5z_updated.trading_partner = mop.trading_partner LEFT JOIN counts ON controlling_ke5z_updated.profit_center = counts.profit_center AND controlling_ke5z_updated.account_number = counts.account_number AND controlling_ke5z_updated.functional_area = counts.functional_area AND controlling_ke5z_updated.trading_partner = counts.trading_partner AND controlling_ke5z_updated.fiscal_year = counts.fiscal_year LEFT JOIN controlling_accruals ON controlling_ke5z_updated.reference_document = controlling_accruals.reference_document WHERE controlling_ke5z_updated.fiscal_year = {year} AND controlling_ke5z_updated.posting_period IN {posting_periods} AND record_type = 0 UNION SELECT 0, {year}, 'Budget value', 0.0, not_used_mop_keys_with_values.cost_center, not_used_mop_keys_with_values.profit_center, not_used_mop_keys_with_values.local_account, mm_cost_position.account_name, 'dummy', 0.0, not_used_mop_keys_with_values.functional_area, 0, 'dummy', '2020-01-01', not_used_mop_keys_with_values.trading_partner, 0, 0, 0, 'dummy', 0, not_used_mop_keys_with_values.cost_position, mm_cost_position.row_name, not_used_mop_keys_with_values.affectability, 'dummy', not_used_mop_keys_with_values.first_level_mgr, not_used_mop_keys_with_values.second_level_mgr,'dummy', 'dummy', not_used_mop_keys_with_values.poc_gc, 'dummy', 'dummy', 0.0, 'dummy', 'dummy', False, {flexed_budget_months_for_union} FROM not_used_mop_keys_with_values LEFT JOIN mm_cost_position ON mm_cost_position.row_index = not_used_mop_keys_with_values.cost_position AND mm_cost_position.account = not_used_mop_keys_with_values.local_account::integer UNION SELECT 0, {year}, 'Dummy value', 0.0, 'Dummy cost center', 'Dummy profit center', 0, 'Dummy account name', 'dummy', 0.0, 'Dummy area', 0, 'dummy', '2020-01-01', 'Dummy partner', 0, 0, 0, 'dummy', 0, 22, 'Direct labour', 'Ovlivnitelné', 'dummy', 'Zima, Petr', 'Zima, Petr' ,'dummy', 'dummy', 'GC', 'dummy', 'dummy', 0.0, 'dummy', 'dummy', False, {flexed_budget_months_for_union} FROM not_used_mop_keys_with_values"
    

    with connection.cursor() as cursor:
        cursor.execute(custom_query)
        rows = cursor.fetchall()

    flexed_budget_query_months = str([f'flexed_budget_m_{i} = row[{i+33}]' for i in months_range])
    flexed_budget_query_months = flexed_budget_query_months[1:-1]

    Manager_Report.objects.all().delete()

    for row in rows:
        cdict = {}
        cdict['posting_period'] = row[0]
        cdict['fiscal_year'] = row[1]
        cdict['text'] = row[2]
        cdict['in_profit_center_local_currency'] = row[3]
        cdict['cost_center'] = row[4]
        cdict['profit_center'] = row[5]
        cdict['account_number'] = row[6]
        cdict['account_name'] = row[7]
        cdict['purchasing_document'] = row[8]
        cdict['quantity'] = row[9]
        cdict['functional_area'] = row[10]
        cdict['document_number'] = row[11]
        cdict['material'] = row[12]
        cdict['posting_date'] = row[13]
        cdict['trading_partner'] = row[14]
        cdict['reference_document'] = row[15]
        cdict['reference_document_line'] = row[16]
        cdict['document_line'] = row[17]
        cdict['username'] = row[18]
        cdict['purchasing_document_item'] = row[19]
        cdict['cost_position'] = row[20]
        cdict['cost_position_text'] = row[21]
        cdict['affectability'] = row[22]
        cdict['responsibility_group'] = row[23]
        cdict['first_line_manager'] = row[24]
        cdict['second_line_manager'] = row[25]
        cdict['fa_description'] = row[26]
        cdict['fa_group_name'] = row[27]
        cdict['poc_gc'] = row[28]
        cdict['cz_account_name'] = row[29]
        cdict['group_account'] = row[30]
        cdict['flexibility_rate'] = row[31]
        cdict['transaction_description'] = row[32]
        cdict['supplier'] = row[33]
        cdict['accruals'] = row[34]
        for i in months_range:
            cdict[f'flexed_budget_m_{i}'] = row[int(f'{34+i}')]
        for i in range(1, 13):
            cdict[f'actual_m_{i}'] = row[3] if row[0] == i else 0
        cdict['ytd_flexed_budget_m_1'] = cdict['flexed_budget_m_1']
        try:
            cdict['ytd_flexed_budget_m_2'] = cdict['ytd_flexed_budget_m_1'] + (cdict['flexed_budget_m_2'] or 0)
            cdict['ytd_flexed_budget_m_3'] = cdict['ytd_flexed_budget_m_2'] + (cdict['flexed_budget_m_3'] or 0)
            cdict['ytd_flexed_budget_m_4'] = cdict['ytd_flexed_budget_m_3'] + (cdict['flexed_budget_m_4'] or 0)
            cdict['ytd_flexed_budget_m_5'] = cdict['ytd_flexed_budget_m_4'] + (cdict['flexed_budget_m_5'] or 0)
            cdict['ytd_flexed_budget_m_6'] = cdict['ytd_flexed_budget_m_5'] + (cdict['flexed_budget_m_6'] or 0)
            cdict['ytd_flexed_budget_m_7'] = cdict['ytd_flexed_budget_m_6'] + (cdict['flexed_budget_m_7'] or 0)
            cdict['ytd_flexed_budget_m_8'] = cdict['ytd_flexed_budget_m_7'] + (cdict['flexed_budget_m_8'] or 0)
            cdict['ytd_flexed_budget_m_9'] = cdict['ytd_flexed_budget_m_8'] + (cdict['flexed_budget_m_9'] or 0)
            cdict['ytd_flexed_budget_m_10'] = cdict['ytd_flexed_budget_m_9'] + (cdict['flexed_budget_m_10'] or 0)
            cdict['ytd_flexed_budget_m_11'] = cdict['ytd_flexed_budget_m_10'] + (cdict['flexed_budget_m_11'] or 0)
            cdict['ytd_flexed_budget_m_12'] = cdict['ytd_flexed_budget_m_11'] + (cdict['flexed_budget_m_12'] or 0)
        except:
            pass

        try:
            cdict['ytd_actual_m_1'] = cdict['actual_m_1']
            cdict['ytd_actual_m_2'] = cdict['ytd_actual_m_1'] + (cdict['actual_m_2'] or 0)
            cdict['ytd_actual_m_3'] = cdict['ytd_actual_m_2'] + (cdict['actual_m_3'] or 0)
            cdict['ytd_actual_m_4'] = cdict['ytd_actual_m_3'] + (cdict['actual_m_4'] or 0)
            cdict['ytd_actual_m_5'] = cdict['ytd_actual_m_4'] + (cdict['actual_m_5'] or 0)
            cdict['ytd_actual_m_6'] = cdict['ytd_actual_m_5'] + (cdict['actual_m_6'] or 0)
            cdict['ytd_actual_m_7'] = cdict['ytd_actual_m_6'] + (cdict['actual_m_7'] or 0)
            cdict['ytd_actual_m_8'] = cdict['ytd_actual_m_7'] + (cdict['actual_m_8'] or 0)
            cdict['ytd_actual_m_9'] = cdict['ytd_actual_m_8'] + (cdict['actual_m_9'] or 0)
            cdict['ytd_actual_m_10'] = cdict['ytd_actual_m_9'] + (cdict['actual_m_10'] or 0)
            cdict['ytd_actual_m_11'] = cdict['ytd_actual_m_10'] + (cdict['actual_m_11'] or 0)
            cdict['ytd_actual_m_12'] = cdict['ytd_actual_m_11'] + (cdict['actual_m_12'] or 0)
        except:
            pass
        if cdict[f'ytd_actual_m_{last_month}'] + cdict[f'ytd_flexed_budget_m_{last_month}'] == 0:
            continue

        Manager_Report.objects.create(**cdict)

        manager_report_new_count = Manager_Report.objects.all().count()

    return HttpResponse(custom_query)


@csrf_exempt
def get_sql_query(request):

    password = request.POST.get('password', None)
    print(password)
    user = request.POST.get('name')
    last_month = request.POST.get('month')

    print(user)

    if authenticate(user, password):
        manager = get_manager(user)
        if manager.excluded_cost_positions:
            excluded_cost_positions = "(" + str(manager.excluded_cost_positions)[1:-1] + ")"
        else:
            excluded_cost_positions = None

        cost_centers = "(" + str(manager.cost_centers)[1:-1] + ")"

    else:
        return HttpResponse("Prihlaseni se nezdarilo")

    if excluded_cost_positions:
        custom_query = f"SELECT * FROM controlling_manager_report WHERE cost_center IN {cost_centers} AND cost_position NOT IN {excluded_cost_positions}"
    else:
        custom_query = f"SELECT * FROM controlling_manager_report WHERE cost_center IN {cost_centers}"

    if user == "Kubin, Rudolf":
        custom_query += "UNION SELECT * FROM controlling_manager_report WHERE cost_position IN ('15', '17', '28')"

    return HttpResponse(custom_query)


@csrf_exempt
def get_sql_query_general(request):

    password = request.POST.get('password', None)
    user = request.POST.get('name')
    last_month = request.POST.get('month')

    if authenticate(user, password):
        manager = get_manager(user)
        excluded_cost_positions = "(" + str(manager.excluded_cost_positions)[1:-1] + ")"
        cost_centers = "(" + str(manager.cost_centers)[1:-1] + ")"
    else:
        return HttpResponse("Prihlaseni se nezdarilo")

    custom_query = f"SELECT posting_period, fiscal_year, affectability, cost_center, cost_position, cost_position_text, first_line_manager, second_line_manager, in_profit_center_local_currency, flexed_budget_m_1,flexed_budget_m_2,flexed_budget_m_3,flexed_budget_m_4,flexed_budget_m_5,flexed_budget_m_6,flexed_budget_m_7,flexed_budget_m_8,flexed_budget_m_9,flexed_budget_m_10,flexed_budget_m_11,flexed_budget_m_12, actual_m_1, actual_m_2, actual_m_3, actual_m_4, actual_m_5, actual_m_6, actual_m_7, actual_m_8, actual_m_9, actual_m_10, actual_m_11, actual_m_12, ytd_flexed_budget_m_1, ytd_flexed_budget_m_2, ytd_flexed_budget_m_3, ytd_flexed_budget_m_4, ytd_flexed_budget_m_5, ytd_flexed_budget_m_6, ytd_flexed_budget_m_7, ytd_flexed_budget_m_8, ytd_flexed_budget_m_9, ytd_flexed_budget_m_10, ytd_flexed_budget_m_11, ytd_flexed_budget_m_12, ytd_actual_m_1, ytd_actual_m_2, ytd_actual_m_3, ytd_actual_m_4, ytd_actual_m_5, ytd_actual_m_6, ytd_actual_m_7, ytd_actual_m_8, ytd_actual_m_9, ytd_actual_m_10, ytd_actual_m_11, ytd_actual_m_12 FROM controlling_manager_report"

    return HttpResponse(custom_query)

@csrf_exempt
def get_connection_string(request):

    print(request.POST)

    password = request.POST.get('password', None)
    user = request.POST.get('name')

    if authenticate(user, password):
        return HttpResponse("Driver={PostgreSQL Unicode};Server=10.49.34.115;Database=postgres;uid=postgres;pwd=5teveJo85")
    else:
        return HttpResponse("Prihlaseni se nezdarilo")