# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-07 10:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chris', '0028_remove_budget_pay_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='pay_qty',
            field=models.IntegerField(default=0),
        ),
    ]