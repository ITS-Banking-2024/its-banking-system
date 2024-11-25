from django.shortcuts import render

# Create your views here.
from dependency_injector.wiring import inject, Provide
from django.http import HttpResponse, HttpRequest
from django.template import loader

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.services import ITradingService


# Create your views here.

def stock_market(request: HttpRequest,
              trading_service: ITradingService = Provide["trading_service"],):

    template = loader.get_template("stock_trading/dashboard.html")

    # Initialize the context with the logged-in user
    context = {
        "user": request.user,
    }

    return HttpResponse(template.render(context,request))
