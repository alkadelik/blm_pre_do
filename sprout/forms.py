from django import forms
from chris.models import Budget, Bank
from django.forms import DateTimeInput # What is this for?
# from django.utils import timezone
# import datetime
from julius import settings

class DateInput(forms.DateInput):
    input_type = "date"

class BudgetSetupForm(forms.ModelForm):

    class Meta:
        model = Budget
        fields = [
            "title",
            "amount",
            "type",
            "frequency",
            "pay_qty",
            "freq_count",
            "first_date",
        ]
        widgets = {
            "first_date": DateInput()
        }

class LinkBankForm(forms.ModelForm):

    class Meta:
        model = Bank
        fields = [
            "bank",
            "acc_no",
        ]

class NewRecipientForm(forms.Form):
    bank = forms.CharField()
    acc_no = forms.IntegerField()
