# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-01 09:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chris', '0024_bank_bank_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bank',
            old_name='name',
            new_name='holder_name',
        ),
    ]
