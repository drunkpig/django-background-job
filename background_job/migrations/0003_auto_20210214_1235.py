# Generated by Django 2.2.13 on 2021-02-14 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('background_job', '0002_auto_20210214_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djangojob',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]