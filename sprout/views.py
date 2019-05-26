# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from sprout.forms import BudgetSetupForm, LinkBankForm
from django.utils import timezone
from datetime import datetime, timedelta

import requests # requests was installed by pip
# import json

from django.views.decorators.csrf import csrf_exempt


class HomeView(TemplateView):
    template_name = "sprout/home.html"

    def get(self, request):
        form = BudgetSetupForm()
        context = {
            "form": form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = BudgetSetupForm(request.POST)
        if form.is_valid():
            new_budget = form.save(commit=False)
            new_budget.user = request.user
            new_budget.created = timezone.now()
            new_budget.updated = timezone.now()

            # From form:
            # amount, type, first_date, frequency
            # freq_count, status, pay_qty
            amount = form.cleaned_data["amount"]
            frequency = form.cleaned_data["frequency"]
            freq_count = form.cleaned_data["freq_count"]
            pay_qty = form.cleaned_data["pay_qty"]
            first_date = form.cleaned_data["first_date"]
            pay_qty = form.cleaned_data["pay_qty"]

            # Calculated:
            interval = frequency * freq_count
            new_budget.interval = interval
            new_budget.pay_value = amount / pay_qty
            new_budget.final_date = first_date + timedelta(days=(interval*(pay_qty-1)))
            new_budget.save()

            request.session["budget_id"] = new_budget.id

            # Updated on "budget execution view":
            # pay_count, next_date,

            return redirect("sprout:recipient")

            # Below was requried if form was submitting to itself
            # context = {
            #     "form": form,
            # }
            # return render(request, self.template_name, context)

class Recipient(TemplateView):
    template_name = "sprout/recipient.html"

    try:
        current_budget_id = request.session["budget_id"]
        print current_budget_id
    except:
        print "No id"
        # return redirect(reverse("sprout:home")) # or redirect to budget list

    def get(self, request):
        form = LinkBankForm()
        context = {
            "form": form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = LinkBankForm(request.POST)
        if form.is_valid():
            new_recipient = form.save(commit=False)
            # new_recipient.budget = current_budget_id
            new_recipient.created = timezone.now()
            new_recipient.save()

            request.session["current_recipient"] = new_recipient.id
            # Get the current budget
            # Update the recipient of the current budget
            return redirect("sprout:pay") # what is this about?

def pay(request):
    # prevent pay from being called on already funded budget
    user = request.user

    return render(request, "sprout/pay.html")

# class PaymentVerification(TemplateView):
#     template_name = "sprout/"
def payment_verification(request):
    user = request.user
    # budget = Budget.objects.get(id=)

    api = "https://api.paystack.co/transaction/verify/"
    headers = {
        'Authorization': "Bearer sk_test_7cb2764341285a8c91ec4ce0c979070188be9cce",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Host': "api.paystack.co",
        'Connection': "keep-alive",
        'cache-control': "no-cache",
    }

    if request.method == "POST":
        pay_ref = request.POST["pay_ref"]

        url = api + pay_ref
        response = requests.request("GET", url, headers=headers).json()

        pay_status = response["status"]
        if pay_status == True:
            # save pay_ref to db
            # update pay_status = "pay_status"
            # update budget_status in db to 1
            pass
        else:
            # save pay_ref to db
            # update pay_status = "pay_status"
            # Leave budget_status as is (should be 0)
            pass
        print response["status"]

        return redirect("/sprout/") # Not sure why I have to use this. Doesn't seem to do anything
