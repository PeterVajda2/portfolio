from django.db import models

class QM02(models.Model):
    area = models.CharField(max_length=16, blank=True, null=True)
    q2_report_number = models.CharField(max_length=16, blank=True, null=True)
    excel_row = models.IntegerField(blank=True, null=True)
    total_costs = models.FloatField(blank=True, null=True)
    other_costs = models.FloatField(blank=True, null=True)
    line_loss = models.FloatField(blank=True, null=True)
    responsible_department = models.CharField(max_length=16, blank=True, null=True)
    responsible_person = models.CharField(max_length=32, blank=True, null=True)
    reason_comment = models.CharField(max_length=512, blank=True, null=True)
    reason_long_text = models.CharField(max_length=512, blank=True, null=True)
    reduction = models.FloatField(blank=True, null=True)
    to_be_invoiced = models.FloatField(blank=True, null=True)
    extra_costs_code = models.CharField(blank=True, max_length=2)
    resource = models.CharField(blank=True, null=True, max_length=16)
    quantity = models.FloatField(blank=True, null=True)
    unit = models.CharField(blank=True, null=True, max_length=16)
    qm_code = models.CharField(blank=True, null=True, max_length=16)
    uploaded = models.BooleanField(default=False, blank=True, null=True)
    invoice = models.CharField(blank=True, null=True, max_length=255)
    


