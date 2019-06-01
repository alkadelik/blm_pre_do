# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from datetime import date

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    email = models.CharField(max_length=32, default='')
    phone = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender=User)

class Budget(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=30, default='') # name of budget
    amount = models.IntegerField(default=0) # total amount to be set aside
    type = models.BooleanField(default=True) # lump sum or multiple
    interval = models.IntegerField(default=0) # days between disbursements
    frequency = models.IntegerField(default=0) # days(1) or weeks(7)
    freq_count = models.IntegerField(default=0) # count of days or weeks
    pay_value = models.IntegerField(default=0) # amount to be paid at individual disbursement
    pay_qty = models.IntegerField(default=0) # amount to be paid at individual disbursement
    pay_count = models.IntegerField(default=0) # count of last disbursement
    first_date = models.DateField(blank=False, null=False) # date first disbursement should be made
    next_date = models.DateField(null=True, blank=True) # date of next disbursement
    final_date = models.DateField(null=False, blank=True) # date of last disbursement
    budget_status = models.IntegerField(default=0) # budget_entered, paid, active, ended, paused
    pay_ref = models.CharField(max_length=30, null=True) # Payment reference for funding a budget
    pay_status = models.CharField(max_length=10, null=True) # Status of payment attempt
    amount_funded = models.IntegerField(null=True) # amount funded for budget
    recipient = models.ForeignKey("Bank", blank=True, null=True) # actuall account/destination budget is spent on
    created = models.DateTimeField(null=False)
    updated = models.DateTimeField(null=False)

class Bank(models.Model):
    holder_name = models.CharField(max_length=55, default="") # The account holder's name
    bank = models.CharField(max_length=55, default="") # The name of the bank
    bank_code = models.IntegerField(blank=True)
    acc_no = models.IntegerField(blank=True) # The recipient (bank) account number
    created = models.DateTimeField(null=False)
    user = models.ForeignKey(User)

class Token(models.Model):
    token = models.IntegerField(default=0)
    last_4 = models.CharField(max_length=4, default='0000')
