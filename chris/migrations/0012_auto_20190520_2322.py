# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-20 22:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chris', '0011_budget_pay_value'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budget',
            old_name='final_pay',
            new_name='final_date',
        ),
        migrations.RenameField(
            model_name='budget',
            old_name='first_pay',
            new_name='first_date',
        ),
        migrations.RenameField(
            model_name='budget',
            old_name='next_pay',
            new_name='next_date',
        ),
    ]
