from dependency_injector.wiring import inject, Provide
from django.db import models, transaction
from typing import List
from uuid import UUID
from core.models import Account


from core.services import ICustomerService
from customers.models import Customer


class CustomerService(ICustomerService):

    @inject
    def __init__(self, account_service: Provide("account_service")):
        self.account_service = account_service

    def get_by_id(self, id: int) -> models.QuerySet:
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> models.QuerySet:
        try:
            return Customer.objects.get(username=username)
        except Customer.DoesNotExist:
            return None

    def get_customer_accounts(self, customer_id: UUID) -> List[Account]:
        return self.account_service.get_accounts_by_customer_id(customer_id)

    def get_customer_balance(self, customer_id: UUID) -> float:
        pass