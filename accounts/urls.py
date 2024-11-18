from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path('account/<uuid:account_id>/', views.account_detail, name='account_detail'),
]