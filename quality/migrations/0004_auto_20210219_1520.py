# Generated by Django 3.1.1 on 2021-02-19 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quality', '0003_qm02_uploaded'),
    ]

    operations = [
        migrations.AddField(
            model_name='qm02',
            name='item_category',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AddField(
            model_name='qm02',
            name='quantity',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='qm02',
            name='resource',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='qm02',
            name='unit',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
