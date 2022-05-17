from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


class CarProfile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.SET_NULL, null=True, blank=True)
    user_roles = models.JSONField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)


class GroupPermissions(models.Model):
    create_reservation = models.JSONField(blank=True, null=True)
    create_accident = models.JSONField(blank=True, null=True)
    create_repair = models.JSONField(blank=True, null=True)
    approve_repair = models.JSONField(blank=True, null=True)
    confirm_repair = models.JSONField(blank=True, null=True)
    close_repair = models.JSONField(blank=True, null=True)
    edit_carpark = models.JSONField(blank=True, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CarProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Car(models.Model):
    shell_number = models.CharField(max_length=30, blank=True, null=True, verbose_name="Shell číslo")
    shell_kb_number = models.CharField(max_length=3, blank=True, null=True, verbose_name="Shell KB číslo")
    pin = models.CharField(max_length=4, blank=True, null=True, verbose_name="PIN")
    car_license_plate = models.CharField(max_length=20, blank=True, null=True, verbose_name="SPZ")
    technical_certificate = models.CharField(max_length=12, blank=True, null=True, verbose_name="Číslo technického průkazu")
    department = models.CharField(max_length=20, blank=True, null=True, verbose_name="Oddělení")
    contract_number = models.CharField(max_length=8, blank=True, null=True, verbose_name="Čislo smlouvy")
    date_init = models.DateTimeField(blank=True, null=True, verbose_name="Datum pořízení")
    leasing_duration = models.IntegerField(blank=True, null=True, verbose_name="Délka leasingu")
    leasing_end = models.DateTimeField(blank=True, null=True, verbose_name="Konec leasingu")
    monthly_payment = models.FloatField(blank=True, null=True, verbose_name="Měsíční platba")
    kms_yearly = models.IntegerField(blank=True, null=True, verbose_name="Km ročně")
    car_price = models.FloatField(blank=True, null=True, verbose_name="Cena")
    pool_car = models.BooleanField(default=False, verbose_name="Pool auto")
    manager_car = models.BooleanField(default=False, verbose_name="Manažer auto")
    car_manufacturer = models.CharField(max_length=50, verbose_name="Výrobce")
    car_make = models.CharField(max_length=50, verbose_name="Model")
    car_mileage = models.IntegerField(blank=True, null=True, verbose_name="Stav km")
    car_status = models.CharField(max_length=30, verbose_name="Status")
    car_information = models.JSONField(blank=True, null=True, verbose_name="Informace")
    car_history = models.JSONField(blank=True, null=True, verbose_name="Historie")
    car_owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, verbose_name="Oddělení/Manažer")
    fuel_consumption_theoretical = models.FloatField(blank=True, null=True, verbose_name="Spotřeba teoretická")
    fuel_consumption_real = models.FloatField(blank=True, null=True, verbose_name="Spotřeba reální")
    repair_ongoing = models.BooleanField(default=False)
    next_service_date = models.DateField(null=True, blank=True)
    next_service_kms = models.IntegerField(null=True, blank=True)
    technical_control_expiry = models.DateField(null=True, blank=True)
    kms_status_current_year = models.IntegerField(null=True, blank=True)


    def get_fields(self):
        return [(field.verbose_name, field.value_from_object(self)) for field in Car._meta.fields if not field.name in ['id', 'car_information', 'car_history', 'car_owner']]

    def get_header(self):
        return [(field.name) for field in self.__class__._meta.fields]



class Reservation(models.Model):
    reservation_datetime_start = models.DateTimeField()
    reservation_datetime_end = models.DateTimeField()
    reserved_car = models.ForeignKey(to=Car, on_delete=models.SET_NULL, null=True)
    reservation_creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, blank=True)
    reservation_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    sequence = models.IntegerField(default=1)
    repair_reservation = models.BooleanField(default=False)
    destination = models.CharField(max_length=250, blank=True, null=True)
    kilometres = models.IntegerField(null=True)

    def get_header(self):
        return [(field.name) for field in self.__class__._meta.fields]


class CarLoan(models.Model):
    reservation = models.ForeignKey(to=Reservation, on_delete=models.SET_NULL, null=True, blank=True)
    car_loaner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, blank=True)
    carloan_start = models.DateTimeField(blank=True, null=True)
    carloan_end = models.DateTimeField(blank=True, null=True)
    closed = models.BooleanField(default=False)


class AccidentReport(models.Model):
    accident_car = models.ForeignKey(to=Car, on_delete=models.SET_NULL, null=True)
    accident_description = models.CharField(max_length=500, blank=True, null=True)
    accident_person = models.ForeignKey(to=User, on_delete=models.SET_NULL, blank=True, null=True)
    driver_role = models.TextField(blank=True, null=True)
    accident_date = models.DateField(blank=True, null=True)
    carloan = models.ForeignKey(to=CarLoan, on_delete=models.SET_NULL, null=True)
    urls = models.JSONField(default=dict)
    repair_created = models.BooleanField(default=False)


class PickupReport(models.Model):
    carloan = models.ForeignKey(to=CarLoan, on_delete=models.SET_NULL, null=True)
    pickup_person = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    pickup_car = models.ForeignKey(to=Car, on_delete=models.SET_NULL, null=True)
    pickup_datetime = models.DateTimeField()
    car_fuel = models.IntegerField(blank=True, null=True)
    car_interior_cleannes = models.IntegerField(blank=True, null=True)
    car_exterior_cleannes = models.IntegerField(blank=True, null=True)
    car_damage = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def get_header(self):
        return [(field.name) for field in self.__class__._meta.fields]


class ReturnReport(models.Model):
    carloan = models.ForeignKey(to=CarLoan, on_delete=models.SET_NULL, null=True)
    return_person = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    returned_car = models.ForeignKey(to=Car, on_delete=models.SET_NULL, null=True)
    return_datetime = models.DateTimeField()
    return_receptionist = models.CharField(max_length=40, blank=True, null=True)
    car_damage = models.CharField(max_length=500)


class CarRepair(models.Model):
    car = models.ForeignKey(to=Car, on_delete=models.SET_NULL, null=True, blank=True)
    carloan = models.ForeignKey(to=CarLoan, on_delete=models.SET_NULL, null=True, blank=True)
    cost_estimate = models.IntegerField(blank=True, null=True)
    repair_cost = models.IntegerField(blank=True, null=True)
    repair_start = models.DateField(blank=True, null=True)
    repair_end = models.DateField(blank=True, null=True)
    end_estimate = models.DateField(blank=True, null=True)
    caused_by_accident = models.BooleanField(default=False)
    caused_by_wear = models.BooleanField(default=False)
    repair_reason = models.TextField(blank=True, null=True)
    srm_number = models.CharField(max_length=50)
    confirmed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    notes = models.CharField(max_length=3500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    reservation = models.ForeignKey(to=Reservation, on_delete=models.SET_NULL, null=True)
    

