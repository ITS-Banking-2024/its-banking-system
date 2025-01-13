from decimal import Decimal
from typing import List
from uuid import UUID
from django.db import transaction
from marshmallow import ValidationError
import yfinance as yf

from core.services import ITradingService
from stock_trading.models import Stock, StockOwnership
from accounts.models import CheckingAccount
from django.apps import apps

from stock_trading.settings import CUSTODY_ACCOUNT_MODEL


def fetch_stock_price(stock_symbol: str) -> Decimal:
    try:
        stock = yf.Ticker(stock_symbol)
        current_price = stock.history(period="1d", interval="1m")["Close"].iloc[-1]
        return Decimal(current_price)
    except Exception as e:
        raise ValidationError(f"Failed to fetch stock price for {stock_symbol}: {str(e)}")


class TradingService(ITradingService):

    def get_stock(self, stock_id: UUID) -> Stock:
        pass

    def get_all_user_stocks(self, account_id: UUID) -> List[Stock]:
        pass

    def get_all_available_stocks(self):
        """
                Fetch all available stocks from the bank's custody account.

                Returns:
                    List[dict]: List of available stocks with details.
        """
        try:
            # Fetch the bank's custody account
            bank_custody_account = apps.get_model(CUSTODY_ACCOUNT_MODEL.split(".")[0], CUSTODY_ACCOUNT_MODEL.split(".")[1]).objects.first()

            if not bank_custody_account:
                raise ValidationError("Bank custody account not found.")

            # Fetch all stocks owned by the custody account
            stock_ownerships = StockOwnership.objects.filter(account=bank_custody_account)

            # Prepare a list of available stocks
            available_stocks = []
            for ownership in stock_ownerships:
                stock = ownership.stock
                available_stocks.append({
                    "id": stock.id,
                    "symbol": stock.symbol,
                    "name": stock.stock_name,
                    "current_price": stock.current_price,
                    "number_available": ownership.quantity,
                })

            return available_stocks

        except Exception as e:
            raise ValidationError(f"Failed to fetch available stocks: {str(e)}")

    def buy_stock(self, account_id: UUID, stock_id: UUID, quantity: int) -> bool:
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")

        try:
            with transaction.atomic():
                # Fetch stock details
                stock = Stock.objects.get(pk=stock_id)
                stock_price = fetch_stock_price(stock.stock_name)
                total_cost = stock_price * Decimal(quantity)

                # Fetch user's account
                account = CheckingAccount.objects.filter(account_id=account_id).first()
                if not account:
                    raise ValidationError("Account not found.")

                # Ensure sufficient funds
                if account.opening_balance < total_cost:
                    raise ValidationError("Insufficient funds to buy stock.")

                # Deduct cost from the account
                account.opening_balance -= total_cost
                account.save()

                # Update stock ownership
                ownership, created = StockOwnership.objects.get_or_create(account=account, stock=stock)
                ownership.quantity += quantity
                ownership.save()

            return True

        except Exception as e:
            raise ValidationError(f"Stock purchase failed: {str(e)}")

    def sell_stock(self, account_id: UUID, stock_id: UUID, quantity: int) -> bool:
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")

        try:
            with transaction.atomic():
                # Fetch stock details
                stock = Stock.objects.get(pk=stock_id)
                stock_price = fetch_stock_price(stock.stock_name)
                total_revenue = stock_price * Decimal(quantity)

                # Fetch stock ownership
                ownership = StockOwnership.objects.filter(account_id=account_id, stock_id=stock_id).first()
                if not ownership or ownership.quantity < quantity:
                    raise ValidationError("Not enough stock to sell.")

                # Reduce stock quantity
                ownership.quantity -= quantity
                if ownership.quantity == 0:
                    ownership.delete()
                else:
                    ownership.save()

                # Credit revenue to the account
                account = CheckingAccount.objects.filter(account_id=account_id).first()
                if not account:
                    raise ValidationError("Account not found.")
                account.opening_balance += total_revenue
                account.save()

            return True

        except Exception as e:
            raise ValidationError(f"Stock sale failed: {str(e)}")

    def get_current_stock_price(self, stock_symbol: str) -> float:
        return float(fetch_stock_price(stock_symbol))
