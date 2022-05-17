from django.db import models
from django.db.models.deletion import SET_NULL

class CardReader(models.Model):
    card_id = models.CharField(max_length=50)
    time =  models.DateTimeField()

class PartNumber(models.Model):
    productionprocess = models.CharField(max_length=25, null=True, blank=True)
    partnumber = models.CharField(max_length=25, null=True, blank=True)
    sapapotime = models.FloatField(null=True, blank=True)
    saptgmaxtime = models.FloatField(null=True, blank=True)


class DLP3(models.Model):
    ordernumber = models.CharField(max_length=12, blank=True, null=True)
    partnumber = models.CharField(max_length=20, blank=True, null=True)
    machine = models.CharField(max_length=50, blank=True, null=True)
    machine_nickname = models.CharField(max_length=50, blank=True, null=True)
    order_start = models.DateTimeField(null=True, blank=True)
    produced_ok_parts = models.IntegerField(null=True)
    produced_nok_parts = models.IntegerField(null=True)
    total_produced_parts = models.IntegerField(null=True)
    processing_time = models.FloatField(null=True)
    processing_time_co = models.FloatField(null=True)
    processing_time_apo = models.FloatField(null=True)
    setup_time = models.FloatField(null=True)
    setup_time_co = models.FloatField(null=True)
    setup_time_apo = models.FloatField(null=True)
    tgmax_time = models.FloatField(null=True)
    month = models.IntegerField(blank=True, null=True)


class Smartkpi(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    creationtime = models.DateTimeField(db_column='CreationTime')  # Field name made lowercase.
    machine = models.CharField(db_column='Machine', max_length=255)  # Field name made lowercase.
    productiontime = models.DateTimeField(db_column='ProductionTime')  # Field name made lowercase.
    ispartok = models.BooleanField(db_column='isPartOK')  # Field name made lowercase.
    partnumber = models.CharField(db_column='PartNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    serialnumber = models.CharField(db_column='SerialNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    confirmtosap = models.BooleanField(db_column='confirmToSAP')  # Field name made lowercase.
    confirmedtosap = models.BooleanField(db_column='confirmedToSAP')  # Field name made lowercase.
    sapconfirmationresult = models.TextField(db_column='SAPconfirmationResult', blank=True, null=True)  # Field name made lowercase.
    sapoperationnumber = models.CharField(db_column='SAPOperationNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ordernumber = models.CharField(db_column='OrderNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    timeperpartsec = models.FloatField(db_column='timePerPartSec', blank=True, null=True)  # Field name made lowercase.
    scrapreason = models.CharField(db_column='ScrapReason', max_length=255, blank=True, null=True)  # Field name made lowercase.
    isupdated = models.BooleanField(db_column='isUpdated')  # Field name made lowercase.
    numberofparts = models.IntegerField(db_column='numberOfParts')  # Field name made lowercase.
    station = models.CharField(db_column='Station', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'smartKPI'
        unique_together = (('machine', 'station', 'productiontime'),)


class Smartkpiorderkeyvaluedata(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    creationtime = models.DateTimeField(db_column='CreationTime')  # Field name made lowercase.
    propertykey = models.CharField(db_column='PropertyKey', max_length=255, blank=True, null=True)  # Field name made lowercase.
    floatvalue =  models.FloatField(db_column='FloatValue', blank=True, null=True)  # Field name made lowercase.
    textvalue = models.CharField(db_column='TextValue', max_length=65535, blank=True, null=True)  # Field name made lowercase.
    datetimevalue = models.DateTimeField(db_column='DateTimeValue')  # Field name made lowercase.
    isfloatvalue = models.BooleanField(db_column='isFloatValue')  # Field name made lowercase.
    istextvalue = models.BooleanField(db_column='isTextValue')  # Field name made lowercase.
    isdatetimevalue = models.BooleanField(db_column='isDateTimeValue')  # Field name made lowercase.
    system = models.CharField(db_column='System', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ordernumber = models.CharField(db_column='OrderNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    updatetime = models.DateTimeField(db_column='UpdateTime')  # Field name made lowercase.
    plantid = models.CharField(db_column='PlantId', max_length=255, blank=True, null=True)  # Field name made lowercase.
    propertykey1 = models.CharField(db_column='PropertyKey1', max_length=255, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'smartKPIOrderKeyValueData'


class TempSmartkpicvsproductiontargetdetail(models.Model):
    linethingname = models.CharField(db_column='LineThingName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='StartTime', blank=True, null=True)  # Field name made lowercase.
    endtime = models.DateTimeField(db_column='EndTime', blank=True, null=True)  # Field name made lowercase.
    productiontime = models.DateTimeField(db_column='ProductionTime', blank=True, null=True)  # Field name made lowercase.
    counter = models.IntegerField(blank=True, null=True)
    ordernumber = models.CharField(db_column='OrderNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    singleparttargetcount = models.IntegerField(db_column='SinglePartTargetCount', blank=True, null=True)  # Field name made lowercase.
    workingtimeinminutes = models.FloatField(db_column='WorkingTimeInMinutes', blank=True, null=True)  # Field name made lowercase.
    timetoproducepartsinminutes = models.FloatField(db_column='TimeToProducePartsInMinutes', blank=True, null=True)  # Field name made lowercase.
    timeforproducedparts = models.FloatField(db_column='TimeForProducedParts', blank=True, null=True)  # Field name made lowercase.
    processingtime = models.FloatField(db_column='ProcessingTime', blank=True, null=True)  # Field name made lowercase.
    setuptime = models.FloatField(db_column='SetupTime', blank=True, null=True)  # Field name made lowercase.
    creationtime = models.DateTimeField(db_column='CreationTime')  # Field name made lowercase.
    shiftfactorinpercent = models.FloatField(db_column='ShiftFactorInPercent')  # Field name made lowercase.
    sumplannednumberofworkers = models.IntegerField(db_column='SumPlannedNumberOfWorkers')  # Field name made lowercase.
    processnumber = models.FloatField(db_column='ProcessNumber')  # Field name made lowercase.
    fullcyclepartsproduced = models.IntegerField(db_column='FullCyclePartsProduced')  # Field name made lowercase.
    utccreationtime = models.DateTimeField(db_column='UTCCreationTime')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TEMP_SmartKPICVSProductionTargetDetail'
        unique_together = (('linethingname', 'starttime', 'endtime', 'counter'),)


class Smartkpimachinemessagedata(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    creationtime = models.DateTimeField(db_column='CreationTime')  # Field name made lowercase.
    machine = models.CharField(db_column='Machine', max_length=255, blank=True, null=True)  # Field name made lowercase.
    messagetime = models.DateTimeField(db_column='MessageTime')  # Field name made lowercase.
    messagetype1 = models.CharField(db_column='MessageType1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    messagetype2 = models.CharField(db_column='MessageType2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    message = models.CharField(db_column='Message', max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='description', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'smartKPIMachineMessageData'


class Shiftcalendar(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    creationtime = models.DateTimeField(db_column='CreationTime')  # Field name made lowercase.
    plant = models.CharField(db_column='Plant', max_length=255)  # Field name made lowercase.
    machine = models.CharField(db_column='Machine', max_length=255)  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='StartTime')  # Field name made lowercase.
    endtime = models.DateTimeField(db_column='EndTime')  # Field name made lowercase.
    qualifier = models.CharField(db_column='Qualifier', max_length=10)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.
    machine_full_name = models.CharField(db_column='Machine_Full_Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    utilization = models.FloatField(db_column='Utilization')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'shiftCalendar'


class Smartkpiprocessfloatdata(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    creationtime = models.DateTimeField(db_column='CreationTime')  # Field name made lowercase.
    machine = models.CharField(db_column='Machine', max_length=255)  # Field name made lowercase.
    productiontime = models.DateTimeField(db_column='ProductionTime')  # Field name made lowercase.
    procesdatatype = models.CharField(db_column='ProcesDataType', max_length=255)  # Field name made lowercase.
    procesdata = models.FloatField(db_column='ProcesData', blank=True, null=True)  # Field name made lowercase.
    serialnumber = models.CharField(db_column='SerialNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    partnumber = models.CharField(db_column='PartNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ordernumber = models.CharField(db_column='OrderNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    procesdatalsl = models.FloatField(db_column='ProcesDataLSL', blank=True, null=True)  # Field name made lowercase.
    procesdatausl = models.FloatField(db_column='ProcesDataUSL', blank=True, null=True)  # Field name made lowercase.
    isupdated = models.BooleanField(db_column='isUpdated')  # Field name made lowercase.
    unit = models.CharField(db_column='Unit', max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(max_length=255, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    trackingnumber = models.CharField(db_column='TrackingNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    procesdatatype2 = models.CharField(db_column='ProcesDataType2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    partnumberrevision = models.CharField(db_column='PartNumberRevision', max_length=255, blank=True, null=True)  # Field name made lowercase.
    identifier = models.CharField(db_column='Identifier', max_length=255, blank=True, null=True)  # Field name made lowercase.
    procesdataprecision = models.CharField(db_column='ProcesDataPrecision', max_length=255, blank=True, null=True)  # Field name made lowercase.
    procesdatatargetvaluename = models.CharField(db_column='ProcesDataTargetValueName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    procesdatatargetvalue = models.FloatField(db_column='ProcesDataTargetValue', blank=True, null=True)  # Field name made lowercase.
    procesdatalowerlimitname = models.CharField(db_column='ProcesDataLowerLimitName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    procesdataupperlimitname = models.CharField(db_column='ProcesDataUpperLimitName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    procesdatatolerancepos = models.CharField(db_column='ProcesDataTolerancePos', max_length=255, blank=True, null=True)  # Field name made lowercase.
    procesdatatoleranceneg = models.CharField(db_column='ProcesDataToleranceNeg', max_length=255, blank=True, null=True)  # Field name made lowercase.
    procesdatatoleranceposfloat = models.FloatField(db_column='ProcesDataTolerancePosFloat', blank=True, null=True)  # Field name made lowercase.
    procesdatatolerancenegfloat = models.FloatField(db_column='ProcesDataToleranceNegFloat', blank=True, null=True)  # Field name made lowercase.
    processdatatargetvaluetolunit = models.CharField(db_column='ProcessDataTargetValueTolUnit', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'smartKPIProcessFloatData'
        unique_together = (('machine', 'productiontime', 'procesdatatype', 'trackingnumber', 'identifier'),)


class OrderStart(models.Model):
    ordernumber = models.CharField(max_length=30)
    order_start = models.DateTimeField(blank=True, null=True)


class PartNumberEffort(models.Model):
    partnumber = models.CharField(max_length=30)
    effort = models.FloatField()
    machine = models.CharField(max_length=30, blank=True, null=True)


class StandardLineOccupancy(models.Model):
    machine = models.CharField(max_length=30, blank=True, null=True)
    occupancy = models.IntegerField(blank=True, null=True)
    waste = models.FloatField(blank=True, null=True)


class CMCanvas(models.Model):
    user_url = models.CharField(max_length=255, blank=True, null=True)
    canvas_picture_url = models.CharField(max_length=512, blank=True, null=True)
    canvas_picture_width = models.FloatField(blank=True, null=True)
    canvas_picture_height = models.FloatField(blank=True, null=True)
    canvas_x = models.IntegerField(blank=True, null=True)
    canvas_y = models.IntegerField(blank=True, null=True)


class CMElement(models.Model):
    canvas = models.ForeignKey(CMCanvas, on_delete=models.CASCADE)
    width = models.FloatField(blank=True, null=True, default=30)
    height = models.FloatField(blank=True, null=True, default=30)
    from_left = models.FloatField(blank=True, null=True)
    from_top = models.FloatField(blank=True, null=True)
    plc_tag = models.CharField(blank=True, null=True, max_length=255)


class CMElementDisplay(models.Model):
    element = models.ForeignKey(CMElement, on_delete=models.CASCADE)


class CMElementData(models.Model):
    element = models.ForeignKey(CMElement, on_delete=models.CASCADE)
    low_alarm = models.FloatField(blank=True, null=True)
    high_alarm = models.FloatField(blank=True, null=True)
    hour_average = models.FloatField(blank=True, null=True)


class ProductionGroup(models.Model):
    short_line = models.CharField(max_length=255)
    material_number = models.CharField(max_length=255)
    production_group = models.CharField(max_length=255)
    long_line = models.CharField(max_length=255, blank=True, null=True)


class OperatorsData(models.Model):
    machine = models.CharField(max_length=255)
    number_workers = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)


class OperatorsDataEdited(models.Model):
    machine = models.CharField(max_length=255)
    number_workers = models.FloatField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)


class ProductionDataEdited(models.Model):
    machine  = models.CharField(max_length=255)
    produced_pieces = models.IntegerField(blank=True, null=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    order = models.CharField(max_length=32, blank=True, null=True)


class ProductionBoxPlot(models.Model):
    machine = models.CharField(max_length=255)
    material = models.CharField(max_length=255, blank=True, null=True)
    produced_pieces = models.IntegerField(blank=True, null=True)
    number_workers = models.FloatField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    order = models.CharField(max_length=32, blank=True, null=True)


class statisticaldata(models.Model):
    machine = models.CharField(max_length=255)
    material = models.CharField(max_length=255, blank=True, null=True)
    number_workers = models.IntegerField(blank=True, null=True)
    Q10 = models.FloatField(blank=True, null=True)
    Q25 = models.FloatField(blank=True, null=True)
    Q50 = models.FloatField(blank=True, null=True)
    Q75 = models.FloatField(blank=True, null=True)
    Q90 = models.FloatField(blank=True, null=True)
    occurrence = models.IntegerField(blank=True, null=True)
    
class MachinesConverter(models.Model):
    short_name = models.CharField(max_length=16) # OrderKeyValueData
    machine_name = models.CharField(max_length=256) # Jinde
    station_name = models.CharField(max_length=256) # MachineMessageData



# Smartkpimachinemessagedata sloupec Message, hodnota zacina KBMaschMessage.Button.NokPart

class Smartkpimachinestatusdata(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    creationtime = models.DateTimeField(db_column='CreationTime')  # Field name made lowercase.
    machine = models.CharField(db_column='Machine', max_length=255)  # Field name made lowercase.
    statustime = models.DateTimeField(db_column='StatusTime')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=255, blank=True, null=True)  # Field name made lowercase.
    substatus = models.CharField(db_column='SubStatus', max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)
    statustype = models.CharField(db_column='StatusType', max_length=255, blank=True, null=True)  # Field name made lowercase.
    utccreationtime = models.DateTimeField(db_column='UTCCreationTime')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'smartKPIMachineStatusData'

class OrdersReality(models.Model):
    machine = models.CharField(max_length=256)
    order = models.CharField(max_length=32)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)


class OrdersPlanned(models.Model):
    machine = models.CharField(max_length=256)
    order = models.CharField(max_length=32)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)


class NumberOfWorkersPlanned(models.Model):
    machine = models.CharField(max_length=256)
    numberofworkers = models.FloatField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    plannednumberofworkers = models.FloatField(blank=True, null=True)
    

class Infrastructure(models.Model):
    machine = models.CharField(max_length=64, blank=True, null=True)
    meskit_name = models.CharField(max_length=64, blank=True, null=True)
    meskit_ip = models.CharField(max_length=64, blank=True, null=True)
    meskit_mac = models.CharField(max_length=64, blank=True, null=True)
    wifi_plug = models.CharField(max_length=64, blank=True, null=True)
    terminal_ip = models.CharField(max_length=64, blank=True, null=True)
    reboot_in_progress = models.BooleanField(default=False)
    last_restart = models.DateTimeField(auto_now=True)


class FP09_alarm_description(models.Model):
    code = models.CharField(max_length=64, blank=True, null=True, unique=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    group = models.CharField(max_length=256, blank=True)
    color_code = models.CharField(max_length=32, blank=True, default='#000000')


class Tb_fp09_alarms(models.Model):
    DSID = models.BigAutoField(db_column='DSID', primary_key=True)  # Field name made lowercase.
    timestampalarm = models.DateTimeField()
    timestampalarmend = models.DateTimeField()
    alarmtime = models.IntegerField()
    alarmcode = models.CharField(max_length=64, blank=True, null=True, unique=True)
    archived = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'Tb_fp09_alarms'


class Tb_fp09_alarmstext(models.Model):
    DSID = models.BigAutoField(db_column='DSID', primary_key=True)  # Field name made lowercase.
    alarmcode = models.ForeignKey(to=Tb_fp09_alarms, to_field='alarmcode', db_column='alarmcode', on_delete=models.CASCADE)
    alarmtext = models.CharField(max_length=64, blank=True, null=True, unique=True)
    alarmtype = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Tb_fp09_alarmstext'


class Tb_fp09_qd(models.Model):
    dsid = models.AutoField(db_column='DSID', primary_key=True)  # Field name made lowercase.
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

        
        
class Smartkpivalues(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    creationtime = models.DateTimeField(db_column='CreationTime')  # Field name made lowercase.
    machine = models.CharField(db_column='Machine', max_length=255)  # Field name made lowercase.
    kpiname = models.CharField(db_column='KPIName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    kpicalculationbase = models.CharField(db_column='KPICalculationBase', max_length=255, blank=True, null=True)  # Field name made lowercase.
    kpidatetime = models.DateTimeField(db_column='KPIDateTime')  # Field name made lowercase.
    kpifloatvalue = models. FloatField(db_column='KPIFloatValue', blank=True, null=True)  # Field name made lowercase.
    kpidatetimeend = models.DateTimeField(db_column='KPIDateTimeEnd')  # Field name made lowercase.
    kpitimebase = models.CharField(db_column='KPITimeBase', max_length=255, blank=True, null=True)  # Field name made lowercase.
    utccreationtime = models.DateTimeField(db_column='UTCCreationTime')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'smartKPIValues'


class FP09_oee_manual_entries(models.Model):
    entry_date = models.DateField()
    sampling_shift = models.CharField(max_length=16, blank=True, null=True)
    repair_shift = models.CharField(max_length=16, blank=True, null=True)
    station = models.CharField(max_length=16, blank=True, null=True)
    what = models.CharField(max_length=255, blank=True, null=True)
    a3 = models.BooleanField(default=False, blank=True, null=True)


class LineFailureTranslation(models.Model):
    station = models.CharField(max_length=128)
    level1status = models.CharField(max_length=256)
    level2status = models.CharField(max_length=256)
    localizedstatustext = models.CharField(max_length=256)


class NOKReasonsTranslation(models.Model):
    station = models.CharField(max_length=128)
    level1status = models.CharField(max_length=256)
    level2status = models.CharField(max_length=256)
    localizedstatustext = models.CharField(max_length=256)
    timeloss = models.IntegerField(blank=True, null=True)

class DLP115min(models.Model):
    machine = models.CharField(max_length=128)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    dlp1 = models.FloatField()
    order = models.CharField(max_length=128)
    lineprocessingtime = models.FloatField()
    numberofparts = models.IntegerField(blank=True, null=True)

class DLP160min(models.Model):
    machine = models.CharField(max_length=128)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    dlp1 = models.FloatField()
    order = models.CharField(max_length=128)
    lineprocessingtime = models.FloatField()
    numberofparts = models.IntegerField(blank=True, null=True)

class DLP14hrs(models.Model):
    machine = models.CharField(max_length=128)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    dlp1 = models.FloatField()
    order = models.CharField(max_length=128)
    lineprocessingtime = models.FloatField()
    numberofparts = models.IntegerField(blank=True, null=True)

class TbFp09CtSt135(models.Model):
    dsid = models.AutoField(db_column='DSID', primary_key=True)  # Field name made lowercase.
    ordernumber = models.CharField(db_column='OrderNumber', max_length=11)  # Field name made lowercase.
    typenumber = models.CharField(db_column='TypeNumber', max_length=15)  # Field name made lowercase.
    productiontimestamp = models.DateTimeField(db_column='ProductionTimeStamp', blank=True, null=True)  # Field name made lowercase.
    cycletime = models.DecimalField(db_column='CycleTime', max_digits=9, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    archived = models.BooleanField(db_column='Archived', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TB_FP09_CT_St135'


class ThingworxLocalmachinestatusdata(models.Model):
    id = models.BigIntegerField(primary_key=True)
    creationtime = models.CharField(max_length=100, blank=True, null=True)
    machine = models.CharField(max_length=100, blank=True, null=True)
    statustime = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    substatus = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    statustype = models.CharField(max_length=100, blank=True, null=True)
    utccreationtime = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'thingworx_localmachinestatusdata'


class ThingworxLocalsmartkpi(models.Model):
    id = models.BigIntegerField(primary_key=True)
    creationtime = models.CharField(max_length=100, blank=True, null=True)
    machine = models.CharField(max_length=100, blank=True, null=True)
    productiontime = models.CharField(max_length=100, blank=True, null=True)
    ispartok = models.IntegerField(blank=True, null=True)
    partnumber = models.CharField(max_length=100, blank=True, null=True)
    serialnumber = models.CharField(max_length=100, blank=True, null=True)
    confirmtosap = models.IntegerField(blank=True, null=True)
    confirmedtosap = models.IntegerField(blank=True, null=True)
    sapconfirmationresult = models.CharField(max_length=100, blank=True, null=True)
    sapoperationnumber = models.CharField(max_length=100, blank=True, null=True)
    ordernumber = models.CharField(max_length=100, blank=True, null=True)
    timeperpartsec = models.CharField(max_length=100, blank=True, null=True)
    scrapreason = models.CharField(max_length=100, blank=True, null=True)
    isupdated = models.IntegerField(blank=True, null=True)
    numberofparts = models.IntegerField(blank=True, null=True)
    station = models.CharField(max_length=100, blank=True, null=True)
    json = models.CharField(max_length=100, blank=True, null=True)
    utccreationtime = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'thingworx_localsmartkpi'

class MaterialConsumption(models.Model):
    order_number = models.CharField(max_length=16, blank=True, null=True)
    planned_pieces = models.IntegerField(blank=True, null=True)
