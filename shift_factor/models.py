from django.db import models


class Order(models.Model):
    line = models.CharField(max_length=16)
    order_number = models.CharField(max_length=16)
    count = models.IntegerField()
    finished = models.BooleanField(default=False)
    updated = models.DateTimeField('updated', auto_now=True)
    sap_confirmed = models.DateTimeField(null=True)


class OBC_Linka1(models.Model):
    record = models.AutoField(db_column='Record', primary_key=True)  # Field name made lowercase.
    poradiden = models.IntegerField(db_column='PoradiDen', blank=True, null=True)  # Field name made lowercase.
    datum = models.DateTimeField(db_column='Datum', blank=True, null=True)  # Field name made lowercase.
    cas = models.DateTimeField(db_column='Cas', blank=True, null=True)  # Field name made lowercase.
    zakazka = models.CharField(db_column='Zakazka', max_length=15, blank=True, null=True)  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=10, blank=True, null=True)  # Field name made lowercase.
    vcislo = models.CharField(db_column='VCislo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    pripojka = models.CharField(db_column='Pripojka', max_length=5, blank=True, null=True)  # Field name made lowercase.
    otvor = models.CharField(db_column='Otvor', max_length=5, blank=True, null=True)  # Field name made lowercase.
    delkasroubu = models.CharField(db_column='DelkaSroubu', max_length=3, blank=True, null=True)  # Field name made lowercase.
    tesnost = models.CharField(db_column='Tesnost', max_length=4, blank=True, null=True)  # Field name made lowercase.
    prachovka = models.CharField(db_column='Prachovka', max_length=2, blank=True, null=True)  # Field name made lowercase.
    lisovaninok = models.BooleanField(db_column='LisovaniNOK', blank=True, null=True)  # Field name made lowercase.
    otvor1 = models.CharField(db_column='Otvor1', max_length=3, blank=True, null=True)  # Field name made lowercase.
    otvor2 = models.CharField(db_column='Otvor2', max_length=3, blank=True, null=True)  # Field name made lowercase.
    otvor3 = models.CharField(db_column='Otvor3', max_length=3, blank=True, null=True)  # Field name made lowercase.
    otvor4 = models.CharField(db_column='Otvor4', max_length=3, blank=True, null=True)  # Field name made lowercase.
    otvor5 = models.CharField(db_column='Otvor5', max_length=3, blank=True, null=True)  # Field name made lowercase.
    otvor6 = models.CharField(db_column='Otvor6', max_length=3, blank=True, null=True)  # Field name made lowercase.
    zatka1 = models.CharField(db_column='Zatka1', max_length=3, blank=True, null=True)  # Field name made lowercase.
    zatka2 = models.CharField(db_column='Zatka2', max_length=3, blank=True, null=True)  # Field name made lowercase.
    zatka3 = models.CharField(db_column='Zatka3', max_length=3, blank=True, null=True)  # Field name made lowercase.
    zatka4 = models.CharField(db_column='Zatka4', max_length=3, blank=True, null=True)  # Field name made lowercase.
    zatka5 = models.CharField(db_column='Zatka5', max_length=3, blank=True, null=True)  # Field name made lowercase.
    zatka6 = models.CharField(db_column='Zatka6', max_length=3, blank=True, null=True)  # Field name made lowercase.
    vyskatlact = models.FloatField(db_column='VyskaTlacT', blank=True, null=True)  # Field name made lowercase.
    vyskapistt = models.FloatField(db_column='VyskaPistT', blank=True, null=True)  # Field name made lowercase.
    pistnok = models.BooleanField(db_column='PistNOK', blank=True, null=True)  # Field name made lowercase.
    tlacnok = models.BooleanField(db_column='TlacNOK', blank=True, null=True)  # Field name made lowercase.
    vyskatlac = models.FloatField(db_column='VyskaTlac', blank=True, null=True)  # Field name made lowercase.
    dlimits = models.FloatField(db_column='DLimitS', blank=True, null=True)  # Field name made lowercase.
    dlimitf = models.IntegerField(db_column='DLimitF', blank=True, null=True)  # Field name made lowercase.
    hlimits = models.FloatField(db_column='HLimitS', blank=True, null=True)  # Field name made lowercase.
    hlimitf = models.IntegerField(db_column='HLimitF', blank=True, null=True)  # Field name made lowercase.
    s1 = models.FloatField(db_column='S1', blank=True, null=True)  # Field name made lowercase.
    f1 = models.IntegerField(db_column='F1', blank=True, null=True)  # Field name made lowercase.
    s2 = models.FloatField(db_column='S2', blank=True, null=True)  # Field name made lowercase.
    f2 = models.IntegerField(db_column='F2', blank=True, null=True)  # Field name made lowercase.
    s3 = models.FloatField(db_column='S3', blank=True, null=True)  # Field name made lowercase.
    f3 = models.IntegerField(db_column='F3', blank=True, null=True)  # Field name made lowercase.
    s4 = models.FloatField(db_column='S4', blank=True, null=True)  # Field name made lowercase.
    f4 = models.IntegerField(db_column='F4', blank=True, null=True)  # Field name made lowercase.
    s5 = models.FloatField(db_column='S5', blank=True, null=True)  # Field name made lowercase.
    f5 = models.IntegerField(db_column='F5', blank=True, null=True)  # Field name made lowercase.
    tesnostpr = models.FloatField(db_column='TesnostPr', blank=True, null=True)  # Field name made lowercase.
    tesnostbar = models.FloatField(db_column='TesnostBar', blank=True, null=True)  # Field name made lowercase.
    castestu = models.DateTimeField(db_column='CasTestu', blank=True, null=True)  # Field name made lowercase.
    vysledek = models.CharField(db_column='Vysledek', max_length=3, blank=True, null=True)  # Field name made lowercase.
    poradiks = models.BigIntegerField(db_column='PoradiKs', blank=True, null=True)  # Field name made lowercase.
    cislotlac = models.SmallIntegerField(db_column='CisloTlac', blank=True, null=True)  # Field name made lowercase.
    obsluha = models.CharField(db_column='Obsluha', max_length=50, blank=True, null=True)  # Field name made lowercase.
    index_pracovnika = models.IntegerField(db_column='Index_Pracovnika', blank=True, null=True)  # Field name made lowercase.
    paleta = models.SmallIntegerField(db_column='Paleta', blank=True, null=True)  # Field name made lowercase.
    tester = models.SmallIntegerField(db_column='Tester', blank=True, null=True)  # Field name made lowercase.
    cisteni = models.BooleanField(db_column='Cisteni', blank=True, null=True)  # Field name made lowercase.
    prujezdy = models.SmallIntegerField(db_column='Prujezdy', blank=True, null=True)  # Field name made lowercase.
    odsroubovani = models.SmallIntegerField(db_column='Odsroubovani', blank=True, null=True)  # Field name made lowercase.
    plechapp = models.CharField(db_column='PlechAPP', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tlaksila = models.FloatField(db_column='TlakSila', blank=True, null=True)  # Field name made lowercase.
    tlaktes = models.FloatField(db_column='TlakTes', blank=True, null=True)  # Field name made lowercase.
    momentbocni = models.FloatField(db_column='MomentBocni', blank=True, null=True)  # Field name made lowercase.
    momentcelni = models.FloatField(db_column='MomentCelni', blank=True, null=True)  # Field name made lowercase.
    kodchyby = models.IntegerField(db_column='KodChyby', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'OBC_Linka1'


class Productioncounts(models.Model):
    line = models.CharField(db_column='Line', max_length=10, blank=True, null=True)  # Field name made lowercase.
    ordernumber = models.CharField(db_column='OrderNumber', max_length=11, blank=True, null=True)  # Field name made lowercase.
    typenumber = models.CharField(db_column='TypeNumber', max_length=13, blank=True, null=True)  # Field name made lowercase.
    orderpcs = models.SmallIntegerField(db_column='OrderPcs', blank=True, null=True)  # Field name made lowercase.
    okpcs = models.SmallIntegerField(db_column='OKPcs', blank=True, null=True)  # Field name made lowercase.
    restpcs = models.SmallIntegerField(db_column='RestPcs', blank=True, null=True)  # Field name made lowercase.

    timeoflastupdate = models.DateTimeField(db_column='TimeOfLastUpdate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ProductionCounts'


class RobotSchedule(models.Model):
    order_number = models.CharField(max_length=18)
    target_quantity = models.IntegerField(default=0)
    type_number = models.CharField(max_length=255, blank=True)
    current_sap_quantity = models.IntegerField(default=0)
    current_sql_quantity = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    sap_update_time = models.DateTimeField(null=True)
    sql_update_time = models.DateTimeField(null=True)
    order_closed = models.BooleanField(default=False)
    group_id = models.CharField(max_length=255)
    sap_max = models.IntegerField(default=0)
