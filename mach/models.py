from django.db import models

class Station(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

class Downtime(models.Model):
    downtime = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=32, default='rgb(157 157 157)')

class DowntimeFromLine(models.Model):
    uid = models.BigIntegerField()
    station = models.ForeignKey(to=Station, on_delete=models.SET_NULL, null=True)
    downtime = models.ForeignKey(to=Downtime, on_delete=models.SET_NULL, null=True)
    beginning_t = models.DateTimeField()
    end_t = models.DateTimeField(null=True)
    comment = models.CharField(max_length=512, blank=True, null=True)