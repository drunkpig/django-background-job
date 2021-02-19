# Generated by Django 3.1.6 on 2021-02-19 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('background_job', '0007_auto_20210218_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='delayedjob',
            name='enable',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='djangojob',
            name='enable',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='jobexechistory',
            name='result',
            field=models.TextField(blank=True, verbose_name='执行返回结果'),
        ),
        migrations.AlterField(
            model_name='djangojob',
            name='trigger_type',
            field=models.CharField(choices=[['cron', 'cron'], ['interval', 'interval'], ['once', 'once'], ['boot_once', 'boot_once']], max_length=128),
        ),
        migrations.AlterField(
            model_name='jobexechistory',
            name='status',
            field=models.CharField(choices=[['New', 'New'], ['Running', 'Running'], ['Success', 'Success'], ['Error!', 'Error!']], max_length=50),
        ),
    ]