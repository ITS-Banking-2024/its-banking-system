import uuid

from dependency_injector.wiring import inject, Provide
from django.http import Http404, JsonResponse
from django.http import HttpRequest
from django.shortcuts import render
from marshmallow import ValidationError

from accounts.forms import TransactionForm, SavingsTransactionForm
from accounts.models import CheckingAccount, SavingsAccount, CustodyAccount
from core.services import ITransactionService, IAccountService


@inject
def account_detail(request, account_id, account_service: IAccountService = Provide["account_service"]):
    # Try to find the account in all concrete account models
    account = account_service.get_account(account_id)
    if not account:
        raise Http404("Account not found.")

    balance = account_service.get_balance(account_id)

    return render(request, 'accounts/account_details.html', {'account': account, 'balance': balance})


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

                account_service.validate_accounts_for_transaction(amount, sending_account_id, receiving_account_id)
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

@inject
def new_atm_transaction(
    request: HttpRequest,
    account_id,
    transaction_service: ITransactionService = Provide["transaction_service"],
    account_service: IAccountService = Provide["account_service"],
):
    """
    Handle ATM transactions, allowing withdrawals for checking accounts.
    """
    if request.method == "POST":
        try:
            # Extract form data
            form_data = request.POST
            pin = form_data.get("pin")
            amount = float(form_data.get("amount"))

            # Validate the account and PIN
            account_service.validate_account_for_atm(amount=amount, account_id=account_id, pin=pin)

            # Perform the ATM transaction
            atm_id = uuid.uuid4()  # Simulate the ATM ID
            transaction_service.create_new_atm_transaction(amount=amount, account_id=account_id, atm_id=atm_id)

            # Render the success screen
            return render(
                request,
                "transactions/atm_success_screen.html",
                {
                    "success": True,
                    "message": f"Transaction of {amount} EUR successful!",
                    "account_id": account_id,
                },
            )

        except ValidationError as e:
            # Render failure screen for validation errors
            return render(
                request,
                "transactions/atm_success_screen.html",
                {
                    "success": False,
                    "message": str(e),
                    "account_id": account_id,
                },
            )
        except Exception as e:
            # Render failure screen for unexpected errors
            return render(
                request,
                "transactions/atm_success_screen.html",
                {
                    "success": False,
                    "message": f"An unexpected error occurred: {str(e)}",
                    "account_id": account_id,
                },
            )
    else:
        # Render the ATM transaction form
        return render(request, "transactions/atm_transaction_form.html", {"account_id": account_id})

def success_screen(request: HttpRequest, success: bool, message: str, account_id):
    return render(request, 'transactions/success_screen.html', {
        "success": success,
        "message": message,
        "account_id": account_id
    })
@inject
def history(
    request: HttpRequest,
    account_id,
    transaction_service: ITransactionService = Provide["transaction_service"],
    account_service: IAccountService = Provide["account_service"],
):
    timeframe = request.GET.get("timeframe", "all_time")

    # Fetch the account object
    account = account_service.get_account(account_id)
    if not account:
        raise Http404("Account not found.")

    # Fetch transaction history
    transaction_history = transaction_service.get_transaction_history(account_id, timeframe)
    for transaction in transaction_history:
        if transaction["receiving_account_id"] == "None":
            transaction["receiving_account_id"] = "ATM Withdrawal"

    totals = account_service.get_account_totals(account_id, timeframe)

    # Prepare context for rendering
    context = {
        "account": account,
        "transaction_history": transaction_history,
        "selected_timeframe": timeframe,
        "total_received": totals["total_received"],
        "total_sent": totals["total_sent"],
    }

    return render(request, "accounts/transaction_history.html", context)

@inject
def savings(request: HttpRequest, account_id, transaction_service: ITransactionService = Provide["transaction_service"], account_service: IAccountService = Provide["account_service"]):
    account = account_service.get_account(account_id)
    if request.method == "POST":
        form = SavingsTransactionForm(request.POST)
        if form.is_valid():
            savings_account_id = account_id
            transaction_type = form.cleaned_data["transaction_type"]
            amount = form.cleaned_data["amount"]

            try:
                if transaction_type == "deposit":
                    account_service.deposit_savings(savings_account_id, amount)
                elif transaction_type == "withdraw":
                    account_service.withdraw_savings(savings_account_id, amount)
                else:
                    raise ValidationError("Invalid transaction type.")

                return render(request, "transactions/success_screen.html", {
                    "success": True,
                    "message": f"{transaction_type.capitalize()} successful!",
                    "account_id": account_id
                })

            except ValidationError as e:
                return render(request, "transactions/success_screen.html", {
                    "success": False,
                    "message": str(e),
                    "account_id": account_id
                })

    else:
        form = SavingsTransactionForm()

    return render(request, "accounts/savings_transaction.html", {"form": form, "account_id": account_id, "balance": account_service.get_balance(account_id), "available_funds": account_service.get_balance(account.reference_account_id)})