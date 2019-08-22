# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from sprout.forms import BudgetSetupForm, NewRecipientForm
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.urls import reverse
from chris.models import Budget, Bank

from django.http import JsonResponse
import requests, json # requests was installed by pip

class HomeView(TemplateView):
    template_name = "sprout/home.html"

    # Form to be able to tell what information is requred depending on the mode
    # i.e. one-off or multiple disbursements. For now, we assume multiple
    def post(self, request):
        if request.method == "POST":
            new_budget = Budget()
            new_budget.user = request.user
            new_budget.created = timezone.now()
            new_budget.updated = timezone.now()

            # From form:
            amount = int(request.POST["amount"]) * 100 # amount always in kobo
            next_date = datetime.strptime(request.POST["next_date"], "%Y-%m-%d")
            interval = ""

            new_budget.title = request.POST["title"]
            new_budget.next_date = next_date
            new_budget.mode = request.POST["mode"]
            new_budget.amount = amount # have to override the entry from the model form

            if new_budget.mode == "1": # It means this is a one-off payment
                # No frequency, frequency factor or pay_qty, thus, do not display them
                # Is it tautology setting them to None here even though they were never set
                new_budget.freq_factor = 0
                new_budget.frequency = 0
                new_budget.pay_qty = 1
                new_budget.pay_value = amount
                new_budget.final_date = next_date
                new_budget.save()
            elif new_budget.mode == "0": # Multiple disburesments
                pay_qty = int(request.POST["pay_qty"])
                frequency = request.POST["frequency"]
                freq_factor = int(request.POST["freq_factor"])

                new_budget.freq_factor = freq_factor
                new_budget.frequency = frequency
                new_budget.pay_qty = pay_qty
                new_budget.pay_value = amount/pay_qty
                # The user may be confused as to how the math is done becuase quotient is being used
                # pay_qty = amount//interval

                # convert frequency to number of days (if days, weeks, or 30 days)
                if frequency == "1":
                    global interval
                    interval = 1 * freq_factor
                    new_budget.interval = interval
                elif frequency == "2":
                    global interval
                    interval = 7 * freq_factor
                    new_budget.interval = interval

                new_budget.final_date = next_date + timedelta(days=(interval*(pay_qty-1)))
                new_budget.save()

            request.session["budget_id"] = new_budget.id
            print request.session["budget_id"]

            return redirect("sprout:list_recipients")

        else:
            return render(request, self.template_name)


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
        # recipient_code = respons["data"]["recipient_code"]
        context = {
            "validation": acc_name,
        }
        # how can this acc_name be sent back to user screen to be displayed?
        # and then sent back when form is submitted so it can be entered to db
        # print acc_name
        # print recipient_code
        print response
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
        user_id = request.POST["user_id"] # Figure out the
            # best way to do this
        holder_name = "Smith" # this should be from the validation

        # at this point, a transfer recipient should be created
        url = "https://api.paystack.co/transferrecipient"
        headers = {
            # "Authorization": "Bearer sk_test_7cb2764341285a8c91ec4ce0c979070188be9cce",
            "Authorization": "Bearer sk_live_01ee65297a9ae5bdf8adbe9ae7cdf6163384a00e"
        }

        # This is updating my live user
        data = {
            'type': "nuban",
            'name': holder_name,
            'description': "Budget title",
            'account_number': acc_no,
            'bank_code': bank_code,
            "currency": "NGN",
            "metadata": {
                "job": "Flesh Eater",
            }
        }
        response = requests.post(url, json=data, headers=headers).json()
        recipient_code = response["data"]["recipient_code"]


        new_recipient = Bank(holder_name=holder_name, bank=bank_name,
            bank_code=bank_code, acc_no=acc_no,
            created=timezone.now(), user_id=user_id, recipient_code=recipient_code)
            # recipient_code appears in two Bank and Budget tables: refactor
        new_recipient.save()

        try:
            current_budget_id = request.session["budget_id"]
            budget = Budget.objects.get(id=current_budget_id)
            if budget.recipient_id is None:
                budget.recipient_id = new_recipient.id
                budget.recipient_code = recipient_code
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
        # "What to do if form is not not post?"
        pass

    # return render(request, "sprout/list_recipients.html")
    return redirect("/sprout/")
    # return render(request, "sprout:new_recipient", context)

def link_recipient(request):
    if request.method == "POST":
        recipient_id = request.POST["recipient_id"]
        # Improve below to get recipient_id from form rather than call
        # Bank table
        recipient = Bank.objects.get(id=recipient_id)
        recipient_code = recipient.recipient_code

        try:
            budget_id = request.session["budget_id"]
            budget = Budget.objects.get(id=budget_id)
            budget.recipient_id = recipient_id
            budget.recipient_code = recipient_code
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
        budget = Budget.objects.get(id=current_budget_id)
        user = request.user
        pk = "pk_test_9b841d2e67007aeca304a57442891a06ad312ece"
        email = "user@sprout.com" # should be user's email
        amount = budget.amount # price is always in kobo
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

            if budget.pay_status == "success":
                budget.pay_ref = response["data"]["reference"]
                budget.amount_funded = response["data"]["amount"]
                # check that amount funded equals budget amount
                budget.budget_status = 1
                budget.save()
                del request.session["budget_id"]
            else:
                # Wait for webhook
                budget.pay_ref = response["data"]["reference"]

        return redirect("/sprout/")
        # Not sure why I have to use this. Doesn't seem to do anything

# Have a history of budgets being funded (similar to TuGs payment history)

def transfer(request):
    url = "https://api.paystack.co/transfer/bulk"
    headers = {
        # "Authorization": "Bearer sk_test_7cb2764341285a8c91ec4ce0c979070188be9cce",
        "Authorization": "Bearer sk_live_01ee65297a9ae5bdf8adbe9ae7cdf6163384a00e"
    }

    # Consider making it such that all budgets that are stored in the db where a next_date
    # must have been funded, or are purged at some point. This saves us from filtering
    # non-serious budgets

    today = datetime.today()
    due_payments = Budget.objects.filter(budget_status__gte=1, budget_status__lt=3,
        next_date__year=today.year,
        next_date__month=today.month,
        next_date__day=today.day
        )
        # Is there an advantage to also filter by pay_count < pay_qty
        # or does the status filter suffice for this?

    transfers = []
    to_update = []
    for budget in due_payments:
        # transfers = [{}, {}]
        transfer = {"amount": budget.pay_value, "recipient": budget.recipient_code}
        params = {
            "budget_id": budget.id,
            "budget_title": budget.title, # reserve this for reason
            "budget_status": budget.budget_status,
            "pay_count": budget.pay_count,
            "pay_qty": budget.pay_qty,
            "interval": budget.interval
        }
        transfers.append(transfer)
        to_update.append(params)

    # Sending to the transfers API
    data = {
        "currency": "NGN",
        "source": "balance",
        "transfers": transfers,
    }
    # feedback for Paystack. If one recipient_code is false (or absent),
    # continue with the others na, rather than null everything
    response = requests.post(url, json=data, headers=headers).json()

    # After payment: Update the budget status and next date in db
    if response["status"] == True:
    # Better yet, check that the number of transfers queued is equal to the number of
    # transfers sent i.e. the number in `response["message"]`
        for budget in due_payments:
            # is the order in whicn they are retrieved from the database the same
            # as the order they are here?
            budget.pay_count += 1
            if budget.pay_count < budget.pay_qty:
                budget.budget_status = 2
                budget.next_date = today + timedelta(days=(budget.interval))
                budget.save()
            elif budget.pay_count == budget.pay_qty:
                budget.budget_status = 3
                budget.save()
    else:
        print "Transfers failed with message:", response["message"]

    return redirect(reverse("sprout:home"))
    # return render(request, "sprout/list_recipients.html")
