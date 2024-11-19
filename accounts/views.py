from lib2to3.fixes.fix_input import context

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
            success = False
            try:
                sending_account_id = account_id
                receiving_account_id = form.cleaned_data["receiving_account_id"]
                amount = form.cleaned_data["amount"]

                if not account_service.validate_accounts_for_transaction(amount, sending_account_id, receiving_account_id):
                    raise ValidationError(f"Accounts validation failed.")

                # Use the service to create the transaction
                transaction_service.create_new_transaction(amount, sending_account_id, receiving_account_id)
                success = True

            except ValidationError as e:
                return render(request, 'transactions/success_screen.html', {
                    "success": success,
                    "message": str(e),
                    "account_id": account_id
                })

            return render(request, 'transactions/success_screen.html', {
                "success": success,
                "message": "Transaction created successfully!" if success else "Transaction failed.",
                "account_id": account_id
            })

    else:
        form = TransactionForm()

    return render(request, "accounts/new_transaction.html", {"form": form, "account_id": account_id})


def success_screen(request: HttpRequest, success: bool, message: str, account_id):
    return render(request, 'transactions/success_screen.html', {
        "success": success,
        "message": message,
        "account_id": account_id
    })
@inject
def history(request: HttpRequest, account_id, transaction_service: ITransactionService = Provide["transaction_service"], account_service: IAccountService = Provide["account_service"]):
    timeframe = request.GET.get("timeframe", "all_time")

    account = (
            CheckingAccount.objects.filter(account_id=account_id).first()
            or SavingsAccount.objects.filter(account_id=account_id).first()
            or CustodyAccount.objects.filter(account_id=account_id).first()
    )
    if not account:
        raise Http404("Account not found.")

    transaction_history = transaction_service.get_transaction_history(account_id, timeframe)

    context = {'account': account, 'transaction_history': transaction_history, 'selected_timeframe': timeframe}

    return render(request, 'accounts/transaction_history.html', context)
