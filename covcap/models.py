from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField


class Action(models.Model):
    project_number = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=180)
    owner = models.CharField(max_length=60, null=True, blank=True)
    responsible = models.CharField(max_length=60, null=True, blank=True)
    type = models.CharField(max_length=10, verbose_name="Department")
    savings_start = models.DateField(null=True, blank=True)
    savings_till = models.DateField(null=True, blank=True)
    savings_per_month = models.FloatField(blank=True, null=True)
    savings_per_year = models.FloatField(blank=True, null=True, default=0)
    savings_actual_year = models.FloatField(blank=True, null=True)
    real_savings_so_far = models.FloatField(blank=True, null=True)
    doi = models.IntegerField(null=True, blank=True)
    comments = models.CharField(max_length=1500, null=True, blank=True)
    risk = models.CharField(max_length=500, null=True, blank=True)
    priority = models.IntegerField(blank=True, null=True)
    one_timer = models.BooleanField(default=False)
    created_by = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

class PendingDoi(models.Model):
    action = models.ForeignKey(to=Action, on_delete=models.CASCADE, blank=True, null=True)
    previous_doi = models.IntegerField(null=True, blank=True)
    new_doi = models.IntegerField(null=True, blank=True)


class News(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


class NewsItem(models.Model):
    news = models.ManyToManyField(to=News)
    type = models.CharField(max_length=100)
    action = models.ForeignKey(to=Action, on_delete=models.CASCADE)
    text = JSONField()
    read = models.BooleanField(default=False, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=15, blank=True, null=True)
    is_superuser = models.BooleanField(default=False, blank=True, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()