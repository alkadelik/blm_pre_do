# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-04 15:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chris', '0002_bank_budget_token'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='name',
            new_name='user',
        ),
    ]
