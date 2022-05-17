from django.db import models
from django.db.models.fields.related import ForeignKey


class CC_material(models.Model):
    material_number = models.CharField(max_length=255, blank=True, null=True, unique=True)
    summary_group = models.CharField(max_length=255, blank=True, null=True) # ADB summary
    sorting_group = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True) # AIM
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    disabled = models.BooleanField(default=False)
    new = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.material_number}"




class FG_material(models.Model):
    material_number = models.CharField(max_length=255, blank=True, null=True)
    cc_material = models.ForeignKey(to=CC_material, to_field='material_number', on_delete=models.SET_NULL, null=True)
    multiplicator = models.FloatField(blank=True, null=True, default=1)
    created = models.DateTimeField(auto_now_add=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    disassembly_group = models.CharField(max_length=255, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    disabled = models.BooleanField(default=False)

    class Meta:
        unique_together = (('material_number', 'cc_material'),)

    def __str__(self):
        return f"{self.material_number}"

    def __repr__(self):
        return f"{self.material_number}"


class R_material(models.Model):
    material_number = models.CharField(max_length=255, blank=True, null=True, unique=True)
    fg_material = models.ManyToManyField(to=FG_material, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)    
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.material_number}"

    def __repr__(self):
        return f"{self.material_number}"


class Pseudo_R_material(models.Model):
    material_number = models.CharField(max_length=255, blank=True, null=True, unique=True)
    r_material = models.ForeignKey(to=R_material, to_field="material_number", on_delete=models.CASCADE)
    

class Midstep_material(models.Model):
    fg_material = models.ManyToManyField(to=FG_material)
    pseudo_r_material = models.ForeignKey(to=Pseudo_R_material, to_field='material_number', on_delete=models.CASCADE)


class Q3(models.Model):
    order_number = models.CharField(max_length=16, blank=True, null=True)
    assembly = models.CharField(max_length=32, blank=True, null=True)
    defective_quantity = models.FloatField(null=True)
    r_material = models.ManyToManyField(to=R_material)
    cc_material = models.ManyToManyField(to=CC_material)
    damage_code = models.CharField(max_length=16, blank=True)
    damage_description = models.CharField(max_length=255, blank=True)
    fg_material = models.ManyToManyField(to=FG_material)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)  


class RR_sorting(models.Model):
    cc_material = models.ForeignKey(to=CC_material, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.CharField(max_length=128, blank=True, null=True)
    summary_group = models.CharField(max_length=128, blank=True, null=True)
    summary_group_result = models.FloatField(blank=True, null=True)
    sorting_group = models.CharField(max_length=128, blank=True, null=True)
    sorting_group_result = models.FloatField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True) 
    year = models.IntegerField(blank=True, null=True)


class RR_disassembly(models.Model):
    fg_material = models.ForeignKey(to=FG_material, on_delete=models.CASCADE, null=True)
    material_result = models.FloatField(blank=True, null=True)
    category = models.CharField(max_length=128, blank=True, null=True)
    category_result = models.FloatField(blank=True, null=True)
    theoretical_gain = models.IntegerField(blank=True, null=True)
    real_gain = models.IntegerField(blank=True, null=True)
    deffective_quantity = models.IntegerField(blank=True, null=True)
    difference = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True) 
    year = models.IntegerField(blank=True, null=True)


class Q3_codes(models.Model):
    code = models.CharField(max_length=16, blank=True, null=True)
    cz_name = models.CharField(max_length=256, blank=True, null=True)
    en_name  = models.CharField(max_length=256, blank=True, null=True)


class Yfcorer(models.Model):
    cc_material = models.ForeignKey(to=CC_material, to_field='material_number', on_delete=models.SET_NULL, null=True)
    raw_cc_material = models.CharField(max_length=255, blank=True, null=True)
    damage_1 = models.CharField(max_length=255, blank=True, null=True)
    damage_2 = models.CharField(max_length=255, blank=True, null=True)
    damage_3 = models.CharField(max_length=255, blank=True, null=True)
    damage_4 = models.CharField(max_length=255, blank=True, null=True)
    damage_5 = models.CharField(max_length=255, blank=True, null=True)
    core_group = models.CharField(max_length=255, blank=True, null=True)
    coc_description = models.CharField(max_length=255, blank=True, null=True)
    warehouse_flag = models.FloatField(blank=True, null=True)
    change_date = models.DateField(null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)


class OrderDates(models.Model):
    order_number = models.CharField(max_length=255, unique=True)
    order_type = models.CharField(max_length=16, blank=True) 
    order_start_date = models.DateField(blank=True, null=True)
    order_finish_date = models.DateField(blank=True, null=True)
    closed = models.BooleanField(default=False)
    dummy = models.BooleanField(default=False)
    wrong = models.BooleanField(default=False)


class Order(models.Model):
    order_number = models.CharField(max_length=255, unique=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    basic_start_date = models.DateField()
    scheduled_start_time = models.TimeField()
    basic_finish_date = models.DateField()
    order_quantity = models.FloatField()
    quantity_delivered = models.FloatField()
    confirmed_scrap = models.FloatField()
    unit = models.CharField(max_length=4, blank=True, null=True)
    system_status = models.CharField(max_length=255)
    user_status = models.CharField(max_length=32, blank=True, null=True)
    quantity_not_pack = models.FloatField(null=True)
    release_date = models.DateField()
    actual_finish_date = models.DateField(blank=True, null=True)
    mrp_controller = models.CharField(max_length=8)
    order_type = models.CharField(max_length=8)
    confirmation_number = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)


class Operation(models.Model):
    material = models.CharField(max_length=255, blank=True, null=True)
    order = models.ForeignKey(to=Order, to_field='order_number', on_delete=models.CASCADE)
    activity = models.CharField(max_length=4)
    group = models.CharField(max_length=255)
    confirmation = models.CharField(max_length=255)
    workplace = models.CharField(max_length=255)
    operation_short_text = models.CharField(max_length=255)
    control_key = models.CharField(max_length=8)
    operation_quantity = models.FloatField()
    confirmed_yield = models.FloatField()
    scrap = models.FloatField()
    rework = models.FloatField(null=True, blank=True)
    storage_location = models.CharField(max_length=8, blank=True, null=True)
    system_status = models.CharField(max_length=255)
    actual_finish_date = models.DateField(null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)


class Component(models.Model):
    workcenter = models.CharField(max_length=32, blank=True, null=True)
    requirement_date = models.DateField(blank=True, null=True)
    requirement_time = models.TimeField(blank=True, null=True)
    order = models.ForeignKey(to=Order, to_field='order_number', on_delete=models.CASCADE)
    pegged_requirement = models.CharField(max_length=32, blank=True, null=True)
    material = models.CharField(max_length=32)
    material_description = models.CharField(max_length=255, blank=True, null=True)
    requirement_quantity = models.FloatField()
    quantity_withdrawn = models.FloatField()
    open_quantity = models.FloatField()
    storage_type = models.CharField(max_length=8, blank=True, null=True)
    storage_bin = models.CharField(max_length=8, blank=True, null=True)
    shortage = models.FloatField()
    missing_part = models.CharField(max_length=255, blank=True, null=True)
    pegged_requirement_object_cc_material = models.ForeignKey(to=CC_material, on_delete=models.CASCADE, null=True)
    material_object_fg_material = models.ManyToManyField(to=FG_material)
    pegged_requirement_object_r_material = models.ForeignKey(to=R_material, on_delete=models.CASCADE, null=True, related_name='pegged_requirement_r_material_object')
    material_object_r_material = models.ForeignKey(to=R_material, on_delete=models.CASCADE, null=True, related_name='material_r_material_object')
    created = models.DateTimeField(auto_now=True, null=True)