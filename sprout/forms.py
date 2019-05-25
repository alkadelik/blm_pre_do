from django import forms
from chris.models import Budget
from django.forms import DateTimeInput # What is this for?
# from django.utils import timezone
# import datetime
from julius import settings

# Unbound form
# class BudgetSetupForm(forms.Form):
#     post = forms.CharField()

# Model form
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
