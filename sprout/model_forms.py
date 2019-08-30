from django import forms
from chris.models import Budget, Bank
from django.forms import DateTimeInput # What is this for?
# from django.utils import timezone
# import datetime
from blm import settings

class DateInput(forms.DateInput):
    input_type = "date"

class BudgetSetupForm(forms.ModelForm):

    class Meta:
        model = Budget
        fields = [
            "title",
            "amount",
            "mode",
            "freq_factor",
            "frequency",
            "pay_qty",
            "next_date",
        ]
        widgets = {
            "next_date": DateInput(),
            # "title": forms.TextInput(attrs={"class": "input"}),
            # "email": forms.EmailInput(attrs={"class": "input"})
        }

# class LinkBankForm(forms.ModelForm):
#
#     class Meta:
#         model = Bank
#         fields = [
#             "bank",
#             "acc_no",
#         ]

class NewRecipientForm(forms.Form):
    bank = forms.CharField()
    acc_no = forms.IntegerField()
