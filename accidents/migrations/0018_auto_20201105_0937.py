# Generated by Django 3.1.2 on 2020-11-05 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accidents', '0017_auto_20201105_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='correctiveaction',
            name='measure_effectiveness',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
