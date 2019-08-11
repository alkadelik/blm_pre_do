from django.core.management.base import BaseCommand, CommandError
from chris.models import Budget

class Command(BaseCommand):
    help = "Makes funds available for the set budget"

    def add_arguments(self, parser):
        parser.add_argument("budget_id", type=int)

    def handle(self, *args, **options):
        # What confirmation can be received from do_budget to authenticate this?
        try:
            budget_id = options["budget_id"]
            budget = Budget.objects.get(id=budget_id)

            # Get budget
            # Look at parameters
                # disbursement due on this date
                # amount
                # Budget is not expiered/closed (status)
            # Verifiy budget is funded
            # Pay budget
            # Update Status
            # Set next/last date
            # Update pay count
            budget.pay_count += 1
            budget.save()
        except:
            raise CommandError("Budget does not exist") # or not funded, or no auth, etc

        self.stdout.write(self.style.SUCCESS("Successfully updated budget"))
