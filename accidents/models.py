from django.db import models
from burza.models import Worker
from django.contrib.auth.models import User


class HashedPicture(models.Model):
    filename = models.CharField(max_length=500, blank=True)
    hashed_name = models.CharField(max_length=50, null=True)


class AccidentsProfile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.SET_NULL, null=True, blank=True)
    is_admin = models.BooleanField(default=False)


class Accident(models.Model):
    injured = models.ForeignKey(to=Worker, on_delete=models.SET_NULL, null=True)
    dob = models.DateField(blank=True, null=True)
    injured_role = models.CharField(max_length=50)
    bozp_aware = models.BooleanField(default=True)
    on_workplace_since = models.DateField(blank=True, null=True)
    injury_classification = models.CharField(max_length=20)
    count_of_injured = models.IntegerField(null=True, blank=True)
    injured_bodypart = models.CharField(max_length=100)
    injury_type = models.CharField(max_length=100, blank=True)
    accident_injury_type = models.CharField(max_length=100, blank=True)
    accident_datetime = models.DateTimeField(blank=True, null=True)
    accident_description = models.CharField(max_length=500, blank=True)
    hours_worked_before_accident = models.FloatField(blank=True, null=True)
    area = models.CharField(max_length=20)
    place = models.CharField(max_length=50)
    image_urls = models.JSONField(default=dict)
    activity_injury = models.CharField(max_length=500)
    injury_description = models.CharField(max_length=500)
    injury_launcher = models.CharField(max_length=500)
    injury_rootcause = models.CharField(max_length=500)
    injury_rootcause_type  = models.CharField(max_length=50)
    workplace_wrong = models.CharField(max_length=500, blank=True)
    employee_wrong = models.CharField(max_length=500, blank=True)
    accident_influenced_by = models.CharField(max_length=500, blank=True)
    immediate_corrective_measures = models.CharField(max_length=500)
    alcohol_test = models.BooleanField(default=False)
    witnesses = models.CharField(max_length=500, blank=True)
    protocol_datetime = models.DateTimeField(blank=True, null=True)
    protocol_author_role = models.CharField(max_length=50)
    fmea_relevant = models.BooleanField(null=True, blank=True)
    sos_revision = models.DateField(null=True, blank=True)
    fmea_implementation = models.DateField(null=True, blank=True)


class Nearmiss(models.Model):
    reporter = models.ForeignKey(to=Worker, on_delete=models.SET_NULL, null=True)
    reporter_role = models.CharField(max_length=50)
    datetime_of_nearmiss = models.DateTimeField()
    area = models.CharField(max_length=20)
    place = models.CharField(max_length=50)
    image_urls = models.JSONField(default=dict)
    activity_nearmiss = models.CharField(max_length=500)
    nearmiss_description = models.CharField(max_length=500)
    nearmiss_launcher = models.CharField(max_length=500)
    nearmiss_rootcause = models.CharField(max_length=500)
    immediate_corrective_measures = models.CharField(max_length=500)
    protocol_datetime = models.DateTimeField(blank=True, null=True)
    protocol_author_role = models.CharField(max_length=50)
    fmea_relevant = models.BooleanField(null=True, blank=True)
    sos_revision = models.DateField(null=True, blank=True)
    fmea_implementation = models.DateField(null=True, blank=True)


class CorrectiveAction(models.Model):
    accident = models.ForeignKey(to=Accident, on_delete=models.SET_NULL, null=True, blank=True)
    nearmiss = models.ForeignKey(to=Nearmiss, on_delete=models.SET_NULL, null=True, blank=True)
    longterm_corrective_measure = models.CharField(max_length=500, blank=True, null=True)
    measure_implementation_date = models.DateField(null=True, blank=True)
    responsible = models.CharField(max_length=60, blank=True, null=True)
    status = models.IntegerField(null=True, blank=True)
    measure_effectiveness = models.CharField(max_length=500, blank=True, null=True)


class InjuryType(models.Model):
    id_number = models.IntegerField()
    injury_type = models.CharField(max_length=150)


class Bodypart(models.Model):
    id_number = models.IntegerField()
    bodypart = models.CharField(max_length=100)