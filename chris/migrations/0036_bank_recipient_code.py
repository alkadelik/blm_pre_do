# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-22 12:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chris', '0035_auto_20190812_0113'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='recipient_code',
            field=models.CharField(default=0, max_length=20),
            preserve_default=False,
        ),
    ]
