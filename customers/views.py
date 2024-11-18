from django.shortcuts import render
from .models import Customer

# Create your views here.
from dependency_injector.wiring import inject, Provide
from django.http import HttpResponse, HttpRequest
from django.template import loader

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from core.services import ICustomerService


@inject
def dashboard(request: HttpRequest,
              customer_service: ICustomerService = Provide["customer_service"],):

    if not request.user.is_authenticated:
        return redirect("customers:customers_login")

    template = loader.get_template("customers/dashboard.html")

    # Initialize the context with the logged-in user
    context = {
        "user": request.user,
    }

    # Fetch customer accounts using the customer service
    customer_accounts = customer_service.get_customer_accounts(request.user.id)

    # Add accounts to the context
    context.update({
        "customer_accounts": customer_accounts,
    })

    return HttpResponse(template.render(context,request))


def customers_login(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = Customer.objects.get(username=username, password=password)

        # user = authenticate(request, username=username, password=password)


        if user is not None and user.is_active:
            login(request, user)

            return redirect("/customers/dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "customers/customers_login.html")