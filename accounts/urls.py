from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path('<uuid:account_id>/', views.account_detail, name='account_detail'),
    path('<uuid:account_id>/transaction', views.new_transaction, name='new_transaction'),
    path("<uuid:account_id>/atm_transaction/", views.new_atm_transaction, name="new_atm_transaction"),
    path('<uuid:account_id>/history', views.history, name='history'),

    path('<uuid:account_id>/savings', views.savings, name='savings'),


]