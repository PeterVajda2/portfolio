from ssl import Options
from django.db import models
from django.forms import CharField
from django.contrib.auth.models import User

class Line(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Part(models.Model):
    label_1 = models.CharField(max_length=255, null=True)
    label_2 = models.CharField(max_length=255, null=True)
    manufacturing_number = models.CharField(max_length=255, null=True)
    manufacturer = models.CharField(max_length=255, null=True)
    sap_number = models.CharField(max_length=255, null=True)
    part_class = models.CharField(max_length=255, null=True)
    matchcode = models.CharField(max_length=255, null=True)
    produced_part = models.BooleanField(null=True)
    electrical = models.BooleanField(null=True)
    mechanical = models.BooleanField(null=True)
    price = models.CharField(max_length=255, blank=True, null=True)
    delivery_time = models.CharField(max_length=3, null=True, blank=True)
    wearable = models.BooleanField(null=True)


class SpareParts(models.Model):
    line = models.ForeignKey(to=Line,  on_delete=models.SET_NULL, null=True)
    part = models.ForeignKey(to=Part, on_delete=models.SET_NULL, null=True)
    usage_description = models.CharField(max_length=255, null=True)
    station = models.CharField(max_length=255, null=True)
    position = models.CharField(max_length=255, null=True)
    quantity = models.CharField(max_length=255, null=True)
    documentation_label = models.CharField(max_length=255, null=True)
    safety_stock = models.CharField(max_length=16, null=True)
    criticality = models.CharField(max_length=16, null=True)
    recommended_part = models.BooleanField(null=True)


class Columns(models.Model):
    label_cz = models.CharField(max_length=255, null=True)
    label_en = models.CharField(max_length=255, null=True)
    technical_name = models.CharField(max_length=255, null=True)
    part_related = models.BooleanField()
    line_related = models.BooleanField()
    crucial = models.BooleanField()
    visible_by_default = models.BooleanField(default=False)
    is_boolean = models.BooleanField(default=False)


class UserVisible(models.Model):
    column = models.ForeignKey(to=Columns, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    visible = models.BooleanField()

