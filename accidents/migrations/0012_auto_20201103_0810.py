# Generated by Django 3.1.2 on 2020-11-03 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accidents', '0011_auto_20201103_0804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nearmiss',
            name='measures_implementation_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
