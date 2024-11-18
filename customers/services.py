from dependency_injector.wiring import inject, Provide
from django.db import models, transaction
from typing import List
from uuid import UUID
from core.models import Account


from core.services import ICustomerService, IUserService
from customers.models import Customer


class CustomerService(ICustomerService):
    """
        Implementation of the ICustomerService interface for checking if a customer has any credit or not.
    """

    @inject
    def __init__(self, account_service: Provide("account_service")):
        self.account_service = account_service

    def has_credit(self, customer: Customer) -> bool:
        return customer.credit > 0

    def redeem_credit(self, customer: Customer, amount: float) -> bool:
        if transaction.get_connection().in_atomic_block:
            # We are already in an atomic transaction, perform the credit redemption
            return self._perform_credit_redemption(customer, amount)
        else:
            # No active atomic transaction, create one and perform the credit redemption
            # at the end of the transaction, the changes will be committed to the database atomically
            with transaction.atomic():
                return self._perform_credit_redemption(customer, amount)

    def _perform_credit_redemption(self, customer: Customer, amount: float) -> bool:
        # Lock the customer record for update, so that no other transaction can modify it
        customer = Customer.objects.select_for_update().get(pk=customer.pk)

        if customer.credit is not None and customer.credit >= amount:
            customer.credit -= amount
            customer.save()
            # in many other ORMs we do not need to call save() explicitly, as the ORM will keep track of
            # the changes and commit them to the database when the transaction is committed
            # personal remark (bid): Django ORM is not the best ORM out there ...
            return True
        else:
            return False

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

    def check_user_balance(self, user_id):
        pass


class CustomerServiceImpl(IUserService):
    @inject
    def __init__(self, banking_service: Provide("banking_service"), trading_service: Provide("trading_service")):
        self.banking_service = banking_service
        self.trading_service = trading_service

    def login(self):
        pass

    def get_user_info(self):
        pass

    def check_balance(self):
        self.banking_service.check_balance()
        pass