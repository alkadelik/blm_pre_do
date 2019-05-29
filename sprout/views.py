# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from sprout.forms import BudgetSetupForm, LinkBankForm
from django.utils import timezone
from datetime import datetime, timedelta
from django.urls import reverse

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

            return redirect("sprout:add_recipient")

            # Below was requried if form was submitting to itself
            # context = {
            #     "form": form,
            # }
            # return render(request, self.template_name, context)

class NewRecipient(TemplateView):
    template_name = "sprout/new_recipient.html"

    def get(self, request):
        form = LinkBankForm()
        context = {
            "form": form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user_id = request.user.id
        form = LinkBankForm(request.POST)
        if form.is_valid():
            new_recipient = form.save(commit=False)
            new_recipient.user_id = user_id
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
        else:
            # "What to do if form is not valid?"
            pass

class ListRecipients(TemplateView):
    template_name = "sprout/list_recipients.html"

    def get(self, request):
        user_id = request.user.id
        banks = Bank.objects.filter(user_id=user_id)

        context = {
            "banks": banks,
        }
        return render(request, self.template_name, context)

def link_recipient(request):
    if request.method == "POST":
        recipient_id = request.POST["recipient_id"]
        try:
            budget_id = request.session["budget_id"]
            budget = Budget.objects.get(id=budget_id)
            budget.recipient_id = recipient_id
            budget.save()
            return redirect("sprout:pay")
        except:
            print "There is no budget to link recipient to"
        return redirect("sprout:home")

def pay(request):
    try:
        current_budget_id = request.session["budget_id"]
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
    except:
        return redirect("sprout:home") # where else can this redirect?
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

    if request.method == "POST":
        pay_ref = request.POST["pay_ref"]

        url = api + pay_ref
        response = requests.request("GET", url, headers=headers).json()

        pay_status = response["status"]
        if pay_status == True:
            current_budget_id = request.session["budget_id"]
            budget = Budget.objects.get(id=current_budget_id)
            budget.pay_status = response["data"]["status"]
            print budget.pay_status

            if budget.pay_status == "success":
        # if:
        #   ret = {status:True};
        # else:
        #   ret = {status:False}
                budget.pay_ref = response["data"]["reference"]
                budget.amount_funded = response["data"]["amount"]
                budget.budget_status = 1
                budget.save()
                del request.session["budget_id"]
            else:
                budget.pay_ref = response["data"]["reference"]

        return redirect("/sprout/")
        # Not sure why I have to use this. Doesn't seem to do anything

# Have a history of budgets being funded (similar to TuGs payment history)

def transfer(request):
    api = "https://api.paystack.co/transferrecipient"
    # Do all these headers apply for transfer?
    headers = {
        'Authorization': "Bearer sk_test_7cb2764341285a8c91ec4ce0c979070188be9cce",
        'type': "nuban",
        'name': "Zombie",
        'description': "Zombier",
        'account_number': "0113376246",
        'bank_code': "044",
        "currency": "NGN",
        # "metadata": {
        #     "job": "Flesh Eater",
        # }
    }

    url = api
    response = requests.request("GET", url, headers=headers).json()

    transfer_status = response["status"]
    return redirect(reverse("sprout:transfer"))
