# Generated by Django 3.1.2 on 2021-07-29 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quality', '0006_qm02_reason_long_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='qm02',
            name='invoice',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
