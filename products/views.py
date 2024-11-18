from dependency_injector.wiring import inject, Provide
from django.http import HttpResponse, HttpRequest
from django.template import loader

from core.services import IProductService


@inject
def index(request: HttpRequest,
          # Provide is a special object used in dependency injection frameworks to specify that the required object
          # should be provided by the framework itself, rather than being instantiated by the code.
          product_service: IProductService = Provide["product_service"], ):
    # get all products from the product service (note that we are not using a concrete product service, but an interface
    products_list = product_service.get_all_products()
    # load the templates and render it with the products list
    template = loader.get_template("products/index.html")
    # the context is a dictionary that is used to pass data to the templates
    context = {
        "products_list": products_list,
    }
    return HttpResponse(template.render(context, request))
