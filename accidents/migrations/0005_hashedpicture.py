# Generated by Django 3.1.2 on 2020-10-27 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accidents', '0004_auto_20201027_0936'),
    ]

    operations = [
        migrations.CreateModel(
            name='HashedPicture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, max_length=500)),
                ('hashed_name', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]
