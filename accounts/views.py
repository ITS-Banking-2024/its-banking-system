from django.http import HttpRequest, HttpResponse, Http404
from accounts.models import Account, CheckingAccount, SavingsAccount, CustodyAccount

from dependency_injector.wiring import inject, Provide

from django.shortcuts import render, redirect
from django.http import HttpRequest
from marshmallow import ValidationError

from core.services import ITransactionService, IAccountService
from accounts.forms import TransactionForm
from django.contrib import messages


def account_detail(request, account_id):
    # Try to find the account in all concrete account models
    account = (
        CheckingAccount.objects.filter(account_id=account_id).first()
        or SavingsAccount.objects.filter(account_id=account_id).first()
        or CustodyAccount.objects.filter(account_id=account_id).first()
    )

    # If account is still None, raise a 404 error
    if not account:
        raise Http404("Account not found.")

    return render(request, 'accounts/account_details.html', {'account': account})


@inject
def new_transaction(request: HttpRequest, account_id, transaction_service: ITransactionService = Provide["transaction_service"], account_service: IAccountService = Provide["account_service"]):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            try:
                sending_account_id = account_id
                receiving_account_id = form.cleaned_data["receiving_account_id"]
                amount = form.cleaned_data["amount"]

                if not account_service.validate_accounts_for_transaction(amount, sending_account_id, receiving_account_id):
                    raise ValidationError(f"Accounts validation failed.")
                # Use the service to create the transaction
                transaction_service.create_new_transaction(amount, sending_account_id, receiving_account_id)

                messages.success(request, "Transaction created successfully!")
                return redirect("accounts:account_detail", account_id=sending_account_id)

            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = TransactionForm()

    return render(request, "accounts/new_transaction.html", {"form": form, "account_id": account_id})

def history(request: HttpRequest, account_id):
    account = (
            CheckingAccount.objects.filter(account_id=account_id).first()
            or SavingsAccount.objects.filter(account_id=account_id).first()
            or CustodyAccount.objects.filter(account_id=account_id).first()
    )
    return render(request, 'accounts/account_details.html', {'account': account})
