from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from django.db import models

from core.models import Account
from core.models import Product
from swd_django_demo.settings import STOCK_MODEL, STOCK_OWNERSHIP_MODEL

"""
In this code, we are defining the interfaces for the services.
Interfaces are abstract classes that declare a set of methods that must be implemented
by any concrete class that implements the interface.
"""


# here we define the interfaces for the services
class IProductService(ABC):
    # Declare abstract methods for ProductService
    @abstractmethod
    def get_all_products(self) -> List[Product]:
        pass

    @abstractmethod
    def get_price(self, product: Product) -> float:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> models.QuerySet:
        pass


class IOrderService(ABC):
    """
    The __init__ method is used in the IOrderService class to initialize an instance of the class.
    It is typically used to set any initial values or attributes that are required by the class.
    In this specific case, it is used to pass an instance of the IProductService class as a parameter
    to the IOrderService constructor.
    This is because the IOrderService class needs to access the get_all_products method of the IProductService class.
    By passing an instance of IProductService to the IOrderService constructor, the IOrderService class can call the
    get_all_products method of the IProductService instance.
    """

    @abstractmethod
    def __init__(self, product_service: IProductService) -> None:
        pass

    @abstractmethod
    def get_all_products(self) -> List[Product]:
        pass

    @abstractmethod
    def get_product(self, product_id: int, product_service: IProductService) -> Product:
        pass


class IAccountService(ABC):
    @abstractmethod
    def get_account(self, account_id: UUID):
        pass

    @abstractmethod
    def get_all_accounts(self) -> List[Account]:
        pass

    @abstractmethod
    def get_accounts_by_customer_id(self, customer_id: UUID) -> List[Account]:
        pass

    @abstractmethod
    def get_bank_custody_account(self):
        pass

    @abstractmethod
    def get_balance(self, account_id: UUID) -> float:
        pass

    @abstractmethod
    def get_account_totals(self, account_id: UUID, timeframe:str) -> dict:
        pass

    @abstractmethod
    def validate_accounts_for_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID) -> bool:
        pass

    @abstractmethod
    def deposit_savings(self, account_id: UUID, amount: float):
        pass

    @abstractmethod
    def withdraw_savings(self, account_id: UUID, amount: float):
        pass


class ICustomerService(ABC):
    @abstractmethod
    def __init__(self, account_service: IAccountService):
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> models.QuerySet:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> models.QuerySet:
        pass

    @abstractmethod
    def get_customer_accounts(self, customer_id: UUID) -> List[Account]:
        pass

    @abstractmethod
    def get_customer_balance(self, customer_id: UUID) -> float:
        pass


class ITransactionService(ABC):

    @abstractmethod
    def create_new_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID) -> bool:
        pass

    @abstractmethod
    def create_new_stock_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID, stock_id: UUID, quantity: int, transaction_type: str) -> bool:
        pass

    @abstractmethod
    def get_transaction_history(self, account_id: UUID, timeframe: str) -> List[dict]:
        pass

    @abstractmethod
    def get_stock_transaction_history(self, account_id: UUID, timeframe: str) -> List[dict]:
        pass


# Interface for Trading Service
class ITradingService(ABC):

    @abstractmethod
    def get_stock(self, stock_id:UUID) -> STOCK_MODEL:
        pass

    @abstractmethod
    def get_all_user_stocks(self, account_id: UUID) -> List[dict]:
        pass

    @abstractmethod
    def get_user_owned_stock(self, account_id: UUID, stock_id: UUID) -> STOCK_OWNERSHIP_MODEL:
        pass

    @abstractmethod
    def get_portfolio_value(self, account_id: UUID) -> float:
        pass

    @abstractmethod
    def get_all_available_stocks(self):
        pass

    @abstractmethod
    def buy_stock(self, account_id: UUID, stock_id: UUID, quantity: int) -> bool:
        pass

    @abstractmethod
    def sell_stock(self, account_id: UUID, stock_id: UUID, quantity: int) -> bool:
        pass

    @abstractmethod
    def get_current_stock_price(self, symbol: str) -> float:
        pass
