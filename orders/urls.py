from django.urls import path

from . import views

app_name = "orders"

# Map URLs to views
urlpatterns = [
    # Map the index URL of the "orders" application to the index view
    path("", views.index, name="index"),
    path("add_to_basket", views.add_to_basket, name="add_to_basket"),
    path("basket_overview", views.basket_overview, name="basket_overview"),
    path("place_oder", views.place_order, name="place_order"),
]