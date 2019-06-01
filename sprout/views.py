# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from sprout.forms import BudgetSetupForm, LinkBankForm, NewRecipientForm
from django.utils import timezone
from datetime import datetime, timedelta
from django.urls import reverse
from chris.models import Budget, Bank

from django.http import JsonResponse
import requests, json # requests was installed by pip



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

            return redirect("sprout:list_recipients")

            # Below was requried if form was submitting to itself
            # context = {
            #     "form": form,
            # }
            # return render(request, self.template_name, context)



#
# class NewRecipient(TemplateView):
#     template_name = "sprout/new_recipient.html"
#
#     def get(self, request):
#         form = LinkBankForm()
#         context = {
#             "form": form,
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request):
#         user_id = request.user.id
#         form = LinkBankForm(request.POST)
#         if form.is_valid():
#             new_recipient = form.save(commit=False)
#             new_recipient.user_id = user_id
#             # new_recipient.budget = current_budget_id
#             new_recipient.created = timezone.now()
#             new_recipient.save()
#
#             try:
#                 current_budget_id = request.session["budget_id"]
#                 budget = Budget.objects.get(id=current_budget_id)
#                 if budget.recipient_id is None:
#                     budget.recipient_id = new_recipient.id
#                     budget.save()
#                     # clear current_budget_id
#                     # del request.session["budget_id"]
#                     return redirect("sprout:pay")
#             except:
#                 # This exception means there is no budget_id set
#                 print "You have successfully added a recipient..."
#             return redirect("sprout:home")
#             # This redirect means there is a budget_id set
#             # but the budget already has a recipient
#             # if the budget hasn't been funded, user can fund
#             # or return recipients list or budget list depending
#             # on where they came from
#         else:
#             # "What to do if form is not valid?"
#             pass

# Populates the recepient (bank) options for users select
class NewRecipient(TemplateView):
    template_name = "sprout/new_recipient.html"


    def get(self, request):
        headers = {
            "Authorization": "Bearer sk_live_01ee65297a9ae5bdf8adbe9ae7cdf6163384a00e",
        }
        bank_list_url = "https://api.paystack.co/bank"
        response = requests.request("GET", bank_list_url, headers=headers).json()

        response = response["data"]

        context = {
            "banks": response,
            "user_id": self.request.user.id , # figure out how best to send this for secuirty
        }
        return render(request, self.template_name, context)

# Verifies that the recipient details (bank and account no) are valid
def resolve_account(request):
    headers = {
        "Authorization": "Bearer sk_live_01ee65297a9ae5bdf8adbe9ae7cdf6163384a00e",
    }

    if request.method == "POST":
        acc_no = request.POST["acc_no"]
        bank_code = request.POST["bank_code"]

        api = "https://api.paystack.co/bank/resolve?account_number="

        api_string = "&bank_code="

        url = api + acc_no + api_string + bank_code
        response = requests.request("GET", url, headers=headers).json()

    try:
        acc_name = response["data"]["account_name"]
        context = {
            "validation": acc_name,
        }
        print acc_name
    except:
        unresolved_message = response["message"]
        context = {
            "validation": unresolved_message,
        }
        print unresolved_message

    # need to figure out how to send this back to the template
    return render(request, "sprout/new_recipient.html", context)

# Adds the new reciient (bank) details to the user's database
# Is this better populated with values from new_recipient.html
# or with values from resolve_account(request)?
def add_recipient(request):
    if request.method == "POST":
        acc_no = request.POST["acc_no"]
        bank_code = request.POST["bank_code"]
        bank_name = request.POST["bank_name"]
        user_id = request.POST["user_id"]
        holder_name = "Debola"

        # print acc_no
        # print bank_code
        # print bank_name
        # print holder_name

        # holder_name = request.POST["holder_name"] # This should be returned by the API
        # acc_no = request.POST["acc_no"]
        # bank_code = request.POST["bank_code"]

        # bank = form.cleaned_data["bank"]
        # acc_no = form.cleaned_data["acc_no"]
        new_recipient = Bank(holder_name=holder_name, bank=bank_name,
            bank_code=bank_code, acc_no=acc_no,
            created=timezone.now(), user_id=user_id)
        new_recipient.save()
    else:
        print "No post"

    # return render(request, "sprout/list_recipients.html")
    return redirect("/sprout/")
    # return render(request, "sprout:new_recipient", context)

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

class ListRecipients(TemplateView):
    template_name = "sprout/list_recipients.html"

    def get(self, request):
        user_id = request.user.id
        banks = Bank.objects.filter(user_id=user_id)

        context = {
            "banks": banks,
        }
        return render(request, self.template_name, context)

def pay(request):
    # request.session["budget_id"] = 22
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
                budget.pay_ref = response["data"]["reference"]
                budget.amount_funded = response["data"]["amount"]
                budget.budget_status = 1
                budget.save()
                del request.session["budget_id"]
            else:
                # Wait for webhook
                budget.pay_ref = response["data"]["reference"]

        return redirect("/sprout/")
        # Not sure why I have to use this. Doesn't seem to do anything

# Have a history of budgets being funded (similar to TuGs payment history)

def transfer_recipient(request):
    url = "https://api.paystack.co/transferrecipient"

    headers = {
        # "Authorization": "Bearer sk_test_7cb2764341285a8c91ec4ce0c979070188be9cce",
        "Authorization": "Bearer sk_live_01ee65297a9ae5bdf8adbe9ae7cdf6163384a00e"
    }
    # This is updating my live user
    data = {
        'type': "nuban",
        'name': "Blessing",
        'description': "Zombier",
        'account_number': "0113376246",
        'bank_code': "058",
        "currency": "NGN",
        "metadata": {
            "job": "Flesh Eater",
        }
    }
    response = requests.post(url, json=data, headers=headers).json()
    print response
    return redirect(reverse("sprout:home"))

def transfer(request):
    url = "https://api.paystack.co/transfer"

    headers = {
        # "Authorization": "Bearer sk_test_7cb2764341285a8c91ec4ce0c979070188be9cce",
        "Authorization": "Bearer sk_live_01ee65297a9ae5bdf8adbe9ae7cdf6163384a00e"
    }
    # This is updating my live user
    data = {
        'source': "balance",
        'reason': "Testing",
        'amount': "5000",
        'recipient': "RCP_ajk0i1kprkw4077",
    }
    response = requests.post(url, json=data, headers=headers).json()
    print response
    return redirect(reverse("sprout:home"))
