from typing import Optional, Union

from django.contrib.auth.base_user import BaseUserManager
from django.db.models import QuerySet
import yfinance as yf
from django.db import transaction
import random
from django.apps import apps

from core.models import Customer
from customers.settings import CHECKING_ACCOUNT_MODEL, CUSTODY_ACCOUNT_MODEL, STOCK_MODEL, STOCK_OWNERSHIP_MODEL


class CustomerManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email for user must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        with transaction.atomic():
            # Create superuser
            user = self.create_user(email, password, **extra_fields)

            CheckingAccount = apps.get_model(CHECKING_ACCOUNT_MODEL.split(".")[0], CHECKING_ACCOUNT_MODEL.split(".")[1])
            CustodyAccount = apps.get_model(CUSTODY_ACCOUNT_MODEL.split(".")[0], CUSTODY_ACCOUNT_MODEL.split(".")[1])
            Stock = apps.get_model(STOCK_MODEL.split(".")[0], STOCK_MODEL.split(".")[1])
            StockOwnership = apps.get_model(STOCK_OWNERSHIP_MODEL.split(".")[0], STOCK_OWNERSHIP_MODEL.split(".")[1])

            # Create CheckingAccount for the superuser
            checking_account = CheckingAccount.objects.create(
                customer_id=user,
                PIN="0000"
            )
            print(f"Created CheckingAccount for superuser: {checking_account}")

            # Create CustodyAccount for the superuser
            custody_account = CustodyAccount.objects.create(reference_account=checking_account, type="custody")
            print(f"Created CustodyAccount for superuser: {custody_account}")

            # Populate CustodyAccount with stocks
            tickers = yf.Tickers(["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"])
            for ticker in tickers.tickers.values():
                try:
                    historical_prices = ticker.history(period='1d', interval='1m')
                    # Get the latest price and time
                    stock_price = historical_prices['Close'].iloc[-1]
                    if stock_price is None:
                        raise ValueError(f"No price found for stock {ticker.ticker}")

                    stock, created = Stock.objects.get_or_create(
                        symbol=ticker.ticker,
                        defaults={
                            "stock_name": ticker.info.get("shortName", "Unknown"),
                            "current_price": stock_price,
                        },
                    )
                    StockOwnership.objects.get_or_create(
                        account=custody_account,
                        stock=stock,
                        defaults={
                            "quantity": random.randint(100, 50000),
                        },
                    )
                    print(f"Added stock {stock.symbol} to CustodyAccount.")
                except Exception as e:
                    print(f"Error adding stock {ticker.ticker}: {str(e)}")

            return user

    def get_by_customer_id(self, customer_id: Union[int, str]) -> Optional[Customer]:
        # Query for Customer object by customer_id (UUID or int)
        qs = self.get_queryset().filter(customer_id=customer_id)
        return qs.first() if qs.exists() else None

    def delete_customer(self, customer_id: Union[int, str]) -> None:
        # Delete a Customer object by customer_id (UUID or int)
        self.get_queryset().filter(customer_id=customer_id).delete()

    def get_all_customers(self) -> QuerySet:
        # Query for all Customer objects
        return self.get_queryset().all()