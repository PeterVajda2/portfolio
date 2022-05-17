from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
import datetime


class CostCenter(models.Model):
    number = models.CharField(max_length=15)
    name = models.CharField(max_length=50)

class Worker(models.Model):
    personal_number = models.IntegerField(unique=True)
    name = models.CharField(max_length=80)
    manager = models.CharField(max_length=80, default="N/A", null=False, blank=False)
    cost_center = models.CharField(max_length=8, blank=True, null=True)
    is_supervisor = models.BooleanField(default=False, null=True, blank=True)
    is_teamleader = models.BooleanField(default=False, null=True, blank=True)
    is_manager = models.BooleanField(default=False, null=True, blank=True)
    not_available = models.BooleanField(default=False, null=True, blank=True)
    costcenter = models.ForeignKey(to=CostCenter, on_delete=models.SET_NULL, blank=True, null=True)
    left = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)
    
class BurzaUser(models.Model):
    burza_user = models.OneToOneField(User, related_name="burza_user", on_delete=models.CASCADE)
    notifications = models.BooleanField(default=False, null=True, blank=True)

class Offer(models.Model):
    worker = models.ForeignKey(to=Worker, on_delete=models.SET_NULL, null=True)
    day = models.DateField()
    shift = models.CharField(max_length=20)
    fullfiled = models.BooleanField(default=False)
    pending_cancellation = models.BooleanField(default=False, blank=True, null=True)
    created_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, blank=True, null=True)
    start = models.DateTimeField(default=now, blank=True)
    end = models.DateTimeField(default=now, blank=True)
    standard = models.BooleanField(default=True, blank=True, null=True)


class Request(models.Model):
    day = models.DateField()
    shift = models.CharField(max_length=20)
    target_costcenter = models.ForeignKey(to=CostCenter, on_delete=models.SET_NULL, blank=True, null=True)
    fullfiled = models.BooleanField(default=False)
    created_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, blank=True, null=True)
    start = models.DateTimeField(default=now, blank=True)
    end = models.DateTimeField(default=now, blank=True)
    standard = models.BooleanField(default=True, blank=True, null=True)


class Assignment(models.Model):
    worker = models.ForeignKey(to=Worker, on_delete=models.SET_NULL, null=True)
    offer = models.ForeignKey(to=Offer, on_delete=models.SET_NULL, blank=True, null=True)
    request = models.ForeignKey(to=Request, on_delete=models.SET_NULL, blank=True, null=True)
    target_costcenter = models.ForeignKey(to=CostCenter, on_delete=models.SET_NULL, blank=True, null=True)
    realised = models.BooleanField(default=True)
    pending_cancellation = models.BooleanField(default=False, blank=True, null=True)
    created_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, blank=True, null=True)
    hours = models.FloatField(blank=True, null=True, default=8)
    assignment_start = models.DateTimeField(blank=True, null=True, default=None)
    assignment_end = models.DateTimeField(blank=True, null=True, default=None)

class PendingRequest(models.Model):
    assignment = models.ForeignKey(to=Assignment, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, blank=True, null=True)
    declined = models.BooleanField(default=False, blank=True, null=True)


@receiver(post_save, sender=User)
def create_burzauser_profile(sender, instance, created, **kwargs):
    if created:
        BurzaUser.objects.create(burza_user=instance)

@receiver(post_save, sender=User)
def save_burzauser_profile(sender, instance, **kwargs):
    instance.burza_user.save()