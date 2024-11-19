from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from datetime import datetime

from django.db import models

from core.models import Product
from core.models import Account

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
    def get_all_accounts(self) -> List[Account]:
        pass

    @abstractmethod
    def get_accounts_by_customer_id(self, customer_id: UUID) -> List[Account]:
        pass

    @abstractmethod
    def get_balance(self, account_id: UUID) -> float:
        pass

    @abstractmethod
    def validate_accounts_for_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID) -> bool:
        pass


class ICustomerService(ABC):
    @abstractmethod
    def __init__(self, account_service: IAccountService):
        pass

    @abstractmethod
    def has_credit(self, customer) -> bool:
        pass

    @abstractmethod
    def redeem_credit(self, customer, amount) -> bool:
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



class IUserService(ABC):
    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def get_user_info(self):
        pass

class ITransactionService(ABC):
    @abstractmethod
    def create_transaction(self, sending_account: Account, receiving_account: Account, amount: float):
        pass

    @abstractmethod
    def update_transaction(self, transaction_id: int, amount: float):
        pass

    @abstractmethod
    def delete_transaction(self, transaction_id: int):
        pass

    @abstractmethod
    def create_new_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID) -> bool:
        pass

    @abstractmethod
    def get_transaction_history(self, account_id: UUID, timeframe: str) -> List[dict]:
        pass


# Interface for Trading Service
class ITradingService(ABC):

    @abstractmethod
    def buy_stock(self, account_id: UUID, stock_id: UUID, quantity: int) -> bool:
        pass

    @abstractmethod
    def sell_stock(self, account_id: UUID, stock_id: UUID, quantity: int) -> bool:
        pass

    @abstractmethod
    def get_current_stock_price(self, stock_id: UUID) -> float:
        pass

# Interface for Online Banking Service
class IOnlineBankingService(ABC):

    @abstractmethod
    def execute_online_transaction(self, transaction_id: UUID) -> bool:
        pass

    @abstractmethod
    def create_online_transaction(self, amount: float, sending_account_id: UUID, receiving_account_id: UUID) -> UUID:
        pass
