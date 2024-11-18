from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, Http404
from accounts.models import Account, CheckingAccount, SavingsAccount, CustodyAccount


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
