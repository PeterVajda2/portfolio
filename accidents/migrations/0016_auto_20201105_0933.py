# Generated by Django 3.1.2 on 2020-11-05 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accidents', '0015_auto_20201105_0916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='correctiveaction',
            name='responsible',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
