# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-19 20:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('chris', '0009_auto_20190519_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='first_pay',
            field=models.DateField(default=datetime.datetime(2019, 5, 19, 20, 50, 51, 166993, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
