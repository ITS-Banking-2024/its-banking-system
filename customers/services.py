from dependency_injector.wiring import inject, Provide
from django.db import models, transaction
from typing import List
from uuid import UUID
from core.models import Account


from core.services import ICustomerService, IUserService
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



class AdminServiceImpl(IUserService):
    def login(self):
        pass

    def get_user_info(self):
        pass

    def create_user(self):
        pass

    def update_user(self):
        pass

    def delete_user(self):
        pass

    def check_user_balance(self, customer_id):
        pass


class CustomerServiceImpl(IUserService):
    @inject
    def __init__(self, banking_service: Provide("transaction_service"), trading_service: Provide("trading_service")):
        self.banking_service = banking_service
        self.trading_service = trading_service

    def login(self):
        pass

    def get_user_info(self):
        pass

    def check_balance(self):
        self.banking_service.check_balance()
        pass