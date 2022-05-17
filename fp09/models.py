from django.db import models

class Station(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

class Downtime(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    station = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)


class DowntimeFromLine(models.Model):
    station = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    downtime = models.CharField(max_length=255, blank=True, null=True)
    beginning_t = models.DateTimeField()
    end_t = models.DateTimeField(null=True)
    comment = models.CharField(max_length=512, blank=True, null=True)
    uploaded_to_xlsx = models.BooleanField(default=False) # neaktualni
    uid = models.CharField(max_length=32, blank=True, null=True) # neaktualni


class CategoryColors(models.Model):
    category = models.CharField(max_length=255, blank=True, null=True)
    color_code = models.CharField(max_length=255, blank=True, null=True)

class TbFp09CtSt135_76(models.Model):
    dsid = models.IntegerField(db_column='DSID', primary_key=True)  # Field name made lowercase.
    ordernumber = models.CharField(db_column='OrderNumber', max_length=11)  # Field name made lowercase.
    typenumber = models.CharField(db_column='TypeNumber', max_length=15)  # Field name made lowercase.
    productiontimestamp = models.DateTimeField(db_column='ProductionTimeStamp', blank=True, null=True)  # Field name made lowercase.
    cycletime = models.DecimalField(db_column='CycleTime', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    archived = models.BooleanField(db_column='Archived', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TB_FP09_CT_St135'


class TbFp09Qd(models.Model):
    dsid = models.IntegerField(db_column='DSID')  # Field name made lowercase.
    ordernumber = models.CharField(db_column='OrderNumber', max_length=11)  # Field name made lowercase.
    typenumber = models.CharField(db_column='TypeNumber', max_length=15)  # Field name made lowercase.
    productiontime = models.DateTimeField(db_column='ProductionTime', blank=True, null=True)  # Field name made lowercase.
    partid = models.CharField(db_column='PartID', max_length=25)  # Field name made lowercase.
    partstatus = models.CharField(db_column='PartStatus', max_length=5, blank=True, null=True)  # Field name made lowercase.
    position = models.SmallIntegerField(db_column='Position', blank=True, null=True)  # Field name made lowercase.
    formerstation = models.SmallIntegerField(db_column='FormerStation', blank=True, null=True)  # Field name made lowercase.
    formerstatus = models.CharField(db_column='FormerStatus', max_length=5, blank=True, null=True)  # Field name made lowercase.
    st010_status = models.SmallIntegerField(db_column='ST010_Status', blank=True, null=True)  # Field name made lowercase.
    st010_result = models.DecimalField(db_column='ST010_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st015_status = models.SmallIntegerField(db_column='ST015_Status', blank=True, null=True)  # Field name made lowercase.
    st015_result = models.DecimalField(db_column='ST015_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st020_status = models.SmallIntegerField(db_column='ST020_Status', blank=True, null=True)  # Field name made lowercase.
    st020_result = models.DecimalField(db_column='ST020_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st030_status = models.SmallIntegerField(db_column='ST030_Status', blank=True, null=True)  # Field name made lowercase.
    st030_result = models.DecimalField(db_column='ST030_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st040_status = models.SmallIntegerField(db_column='ST040_Status', blank=True, null=True)  # Field name made lowercase.
    st040_result = models.DecimalField(db_column='ST040_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st050_status = models.SmallIntegerField(db_column='ST050_Status', blank=True, null=True)  # Field name made lowercase.
    st050_result = models.DecimalField(db_column='ST050_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st060_status = models.SmallIntegerField(db_column='ST060_Status', blank=True, null=True)  # Field name made lowercase.
    st060_result = models.DecimalField(db_column='ST060_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st061_status = models.SmallIntegerField(db_column='ST061_Status', blank=True, null=True)  # Field name made lowercase.
    st061_result = models.DecimalField(db_column='ST061_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st070_status = models.SmallIntegerField(db_column='ST070_Status', blank=True, null=True)  # Field name made lowercase.
    st070_result = models.DecimalField(db_column='ST070_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st080_status = models.SmallIntegerField(db_column='ST080_Status', blank=True, null=True)  # Field name made lowercase.
    st080_result = models.DecimalField(db_column='ST080_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st085_status = models.SmallIntegerField(db_column='ST085_Status', blank=True, null=True)  # Field name made lowercase.
    st085_result = models.DecimalField(db_column='ST085_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st085_etalon = models.IntegerField(db_column='ST085_Etalon', blank=True, null=True)  # Field name made lowercase.
    st090_status = models.SmallIntegerField(db_column='ST090_Status', blank=True, null=True)  # Field name made lowercase.
    st090_result = models.DecimalField(db_column='ST090_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st095_status = models.SmallIntegerField(db_column='ST095_Status', blank=True, null=True)  # Field name made lowercase.
    st095_result = models.DecimalField(db_column='ST095_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st101_status = models.SmallIntegerField(db_column='ST101_Status', blank=True, null=True)  # Field name made lowercase.
    st101_result = models.DecimalField(db_column='ST101_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st102_status = models.SmallIntegerField(db_column='ST102_Status', blank=True, null=True)  # Field name made lowercase.
    st102_result = models.DecimalField(db_column='ST102_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st103_status = models.SmallIntegerField(db_column='ST103_Status', blank=True, null=True)  # Field name made lowercase.
    st103_result = models.DecimalField(db_column='ST103_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st104_status = models.SmallIntegerField(db_column='ST104_Status', blank=True, null=True)  # Field name made lowercase.
    st104_result = models.DecimalField(db_column='ST104_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st105_status = models.SmallIntegerField(db_column='ST105_Status', blank=True, null=True)  # Field name made lowercase.
    st105_result = models.DecimalField(db_column='ST105_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st106_status = models.SmallIntegerField(db_column='ST106_Status', blank=True, null=True)  # Field name made lowercase.
    st106_result = models.DecimalField(db_column='ST106_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st107_status = models.SmallIntegerField(db_column='ST107_Status', blank=True, null=True)  # Field name made lowercase.
    st107_result = models.DecimalField(db_column='ST107_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st110_status = models.SmallIntegerField(db_column='ST110_Status', blank=True, null=True)  # Field name made lowercase.
    st110_result = models.DecimalField(db_column='ST110_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st120_status = models.SmallIntegerField(db_column='ST120_Status', blank=True, null=True)  # Field name made lowercase.
    st120_result = models.DecimalField(db_column='ST120_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st125_status = models.SmallIntegerField(db_column='ST125_Status', blank=True, null=True)  # Field name made lowercase.
    st125_result = models.DecimalField(db_column='ST125_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    st130_status = models.SmallIntegerField(db_column='ST130_Status', blank=True, null=True)  # Field name made lowercase.
    st130_result = models.DecimalField(db_column='ST130_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    archived = models.BooleanField(db_column='Archived', blank=True, null=True)  # Field name made lowercase.
    st135_status = models.SmallIntegerField(db_column='ST135_Status', blank=True, null=True)  # Field name made lowercase.
    st135_result = models.DecimalField(db_column='ST135_Result', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TB_FP09_QD'


class Epoch(models.expressions.Func):
    template = 'EXTRACT(epoch FROM %(expressions)s)::INTEGER'
    output_field = models.IntegerField()


class PairedDowntime(models.Model):
    downtime = models.ForeignKey(to=DowntimeFromLine, on_delete=models.SET_NULL, null=True)
    alarm_code = models.CharField(max_length=128, blank=True, null=True)
    alarm_text = models.CharField(max_length=128, blank=True, null=True)
    alarm_type = models.CharField(max_length=1, blank=True, null=True)
    downtime_duration = models.IntegerField(blank=True, null=True)


class DowntimeFromLineClone(models.Model):
    station = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    downtime = models.CharField(max_length=255, blank=True, null=True)
    beginning_t = models.DateTimeField()
    end_t = models.DateTimeField(null=True)
    comment = models.CharField(max_length=512, blank=True, null=True)
    uploaded_to_xlsx = models.BooleanField(default=False) # neaktualni
    uid = models.CharField(max_length=32, blank=True, null=True) # neaktualni

class StopLineAlarms(models.Model):
    alarmcode_id = models.CharField(max_length=255, blank=True, null=True)
    station = models.CharField(max_length=255, blank=True, null=True)


class TypeDetails(models.Model):
    partnumber = models.CharField(max_length=255, blank=True, null=True)
    konstrukcni_varianta = models.CharField(max_length=255, blank=True, null=True)
    typ_krouzku = models.CharField(max_length=255, blank=True, null=True)
    typ_zavitu = models.CharField(max_length=255, blank=True, null=True)
    barva = models.CharField(max_length=255, blank=True, null=True)


class Counter(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    info = models.CharField(max_length=32)