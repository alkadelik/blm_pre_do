# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from sprout.forms import BudgetSetupForm, LinkBankForm
from django.utils import timezone
from datetime import datetime, timedelta

import requests # requests was installed by pip
# import json
from chris.models import Budget, Bank

# from django.views.decorators.csrf import csrf_exempt


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

            try:
                current_budget_id = request.session["budget_id"]
                budget = Budget.objects.get(id=current_budget_id)
                if budget.recipient_id is None:
                    budget.recipient_id = new_recipient.id
                    budget.save()
                    # clear current_budget_id
                    # del request.session["budget_id"]
                    return redirect("sprout:pay")
            except:
                # This exception means there is no budget_id set
                print "You have successfully added a recipient..."
            return redirect("sprout:home")
            # This redirect means there is a budget_id set
            # but the budget already has a recipient
            # if the budget hasn't been funded, user can fund
            # or return recipients list or budget list depending
            # on where they came from

def pay(request):
    # prevent pay from being called on already funded budget
    user = request.user
    pk = "pk_test_9b841d2e67007aeca304a57442891a06ad312ece"
    email = "user@sprout.com"
    amount = 30000 # price is always in kobo
    currency = "NGN"

    context = {
        "pk": pk,
        "email": email,
        "amount": amount,
        "currency": currency,
    }
    return render(request, "sprout/pay.html", context)

# class PaymentVerification(TemplateView):
#     template_name = "sprout/"
def payment_verification(request):
    api = "https://api.paystack.co/transaction/verify/"
    headers = {
        'Authorization': "Bearer sk_test_7cb2764341285a8c91ec4ce0c979070188be9cce",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Host': "api.paystack.co",
        'Connection': "keep-alive",
        'cache-control': "no-cache",
    }

    # try:
    #     current_budget_id = request.session["budget_id"]
    #     budget = Budget.objects.get(id=current_budget_id)
        # all conditions set e.g. price, user email, etc
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
