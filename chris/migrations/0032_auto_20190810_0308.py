# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-10 02:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chris', '0031_bank_recipient_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='recipient_code',
            field=models.CharField(max_length=20),
        ),
    ]
