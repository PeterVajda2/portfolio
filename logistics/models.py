from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='logistics_profile')
    role = models.CharField(max_length=255, blank=True, null=True, default='Logistics')
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.last_name


class EmailNotification(models.Model):
    profile = models.ForeignKey(to=Profile, on_delete=models.SET_NULL, null=True)
    email = models.CharField(blank=True, max_length=255)
    notify_on_create = models.BooleanField(default=True)
    notify_on_update = models.BooleanField(default=False)
    notify_local_only = models.BooleanField(default=True)
    notify_global = models.BooleanField(default=False)


class ProductionArea(models.Model):
    name = models.CharField(max_length=255, unique=True)
    responsible = models.ManyToManyField(to=Profile, related_name='production_area_responsible')


class Line(models.Model):
    name = models.CharField(max_length=255, unique=True)
    production_area = models.ForeignKey(to=ProductionArea, on_delete=models.SET_NULL, null=True)


class TrainCircuit(models.Model):
    number = models.IntegerField()
    line = models.ForeignKey(to=Line, on_delete=models.SET_NULL, null=True)


class Category(models.Model):
    category = models.CharField(max_length=255, unique=True)


class Subcategory(models.Model):
    subcategory = models.CharField(max_length=255)
    category = models.ForeignKey(to=Category, on_delete=models.SET_NULL, null=True)


class TrainDriver(models.Model):
    train_driver = models.CharField(max_length=255)
    

class Downtime(models.Model):
    downtime_date = models.DateTimeField(verbose_name='Datum')
    shift = models.CharField(max_length=10)
    recorded_by = models.CharField(max_length=255)
    train_circuit = models.ForeignKey(to=TrainCircuit, to_field='id', on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=255)
    material_number = models.CharField(max_length=255)
    is_downtime_by_production = models.BooleanField(default=True)
    is_downtime_by_logistics = models.BooleanField(default=True)
    downtime_start = models.DateTimeField()
    downtime_end = models.DateTimeField()
    train_driver = models.ForeignKey(to=TrainDriver, on_delete=models.SET_NULL, null=True)
    category_by_production = models.ForeignKey(to=Category, on_delete=models.SET_NULL, null=True, related_name='category_by_production')
    subcategory_by_production = models.ForeignKey(to=Subcategory, on_delete=models.SET_NULL, null=True, related_name='subcategory_by_production')
    note_by_production = models.CharField(max_length=512, blank=True, null=True)
    category_by_logistics = models.ForeignKey(to=Category, on_delete=models.SET_NULL, null=True, related_name='category_by_logistics')
    subcategory_by_logistics = models.ForeignKey(to=Subcategory, on_delete=models.SET_NULL, null=True, related_name='subcategory_by_logistics')
    logistics_deduction = models.IntegerField(default=0)
    note_by_logistics = models.CharField(max_length=512, blank=True)
    decoded_by = models.CharField(max_length=255, null=True)
    downtime_rootcause = models.CharField(max_length=512, null=True)
    corrective_action = models.CharField(max_length=255, null=True)
    rca_analysis = models.BooleanField(default=False)
    method_used = models.CharField(max_length=255, null=True)
    responsible = models.CharField(max_length=255, null=True)
    deadline = models.DateField(null=True)
    status = models.FloatField(null=True)
    production_area = models.ForeignKey(to=ProductionArea, on_delete=models.SET_NULL, null=True)
    line = models.ForeignKey(to='Line', to_field='name', on_delete=models.SET_NULL, null=True)
    is_external = models.BooleanField(default=False)
    external_downtime_id = models.IntegerField(null=True)
    external_line = models.CharField(max_length=32, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)


class Shift(models.Model):
    shift_beginning = models.DateTimeField()
    team = models.CharField(max_length=1, null=True, blank=True)