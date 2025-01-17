from typing import List
from uuid import UUID

import yfinance as yf
from dependency_injector.wiring import Provide, inject
from django.utils.timezone import now
from django.db import transaction
from datetime import timedelta
from marshmallow import ValidationError

from core.services import ITradingService
from stock_trading.models import Stock, StockOwnership


def fetch_stock_price(stock_symbol: str) -> float:
    try:
        stock = yf.Ticker(stock_symbol)
        current_price = stock.history(period="1d", interval="1m")["Close"].iloc[-1]
        return round(current_price,2)
    except Exception as e:
        raise ValidationError(f"Failed to fetch stock price for {stock_symbol}: {str(e)}")


class TradingService(ITradingService):

    @inject
    def __init__(self, transaction_service: Provide["transaction_service"], account_service: Provide["account_service"]):
        self.transaction_service = transaction_service
        self.account_service = account_service

    def get_stock(self, stock_id: UUID) -> Stock:
        stock = Stock.objects.get(stockID=stock_id)
        if not stock:
            raise ValidationError(f"Stock {stock_id} does not exist")
        return stock

    def get_all_user_stocks(self, account_id: UUID) -> List[dict]:
        account = self.account_service.get_account(account_id)
        if not account:
            raise ValidationError(f"Account with id {account_id} is not found.")

        ownerships = StockOwnership.objects.filter(account=account)
        if not ownerships:
            return []
        portfolio = [
            {
                "id": str(ownership.stock.stockID),
                "name": ownership.stock.stock_name,
                "symbol": ownership.stock.symbol,
                "quantity": ownership.quantity,
                "current_price": self.get_current_stock_price(ownership.stock.symbol),
                "total_value": round(ownership.quantity * self.get_current_stock_price(ownership.stock.symbol),2),
            }
            for ownership in ownerships
        ]
        return portfolio

    def get_user_owned_stock(self, account_id: UUID, stock_id: UUID) -> StockOwnership:
        account = self.account_service.get_account(account_id)
        stock = self.get_stock(stock_id)
        if not account:
            raise ValidationError(f"Account with id {account_id} is not found.")

        stock_ownership = StockOwnership.objects.filter(account=account, stock=stock).first()
        if not stock_ownership:
            raise ValidationError(f"Account: {account_id} does not have stock {stock_id} owned.")

        return stock_ownership

    def get_portfolio_value(self, account_id: UUID) -> float:
        user_stocks = self.get_all_user_stocks(account_id)
        portfolio_value = 0
        for user_stock in user_stocks:
            portfolio_value += user_stock["total_value"]
        return float(round(portfolio_value,2))



    def get_all_available_stocks(self):
        """
                Fetch all available stocks from the bank's custody account.

                Returns:
                    List[dict]: List of available stocks with details.
        """
        try:
            # Fetch the bank's custody account
            bank_custody_account = self.account_service.get_bank_custody_account()
            if not bank_custody_account:
                raise ValidationError("Bank custody account not found.")

            # Fetch all stocks owned by the custody account
            stock_ownerships = StockOwnership.objects.filter(account=bank_custody_account)

            # Prepare a list of available stocks
            available_stocks = []
            for ownership in stock_ownerships:
                stock = ownership.stock
                available_stocks.append({
                    "id": str(stock.stockID),
                    "symbol": stock.symbol,
                    "name": stock.stock_name,
                    "current_price": self.get_current_stock_price(stock.symbol),
                    "number_available": ownership.quantity,
                })
            return available_stocks
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Failed to fetch available stocks: {str(e)}")

    def buy_stock(self, account_id: UUID, stock_id: UUID, quantity: int) -> bool:
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")

        try:
            with transaction.atomic():
                # Fetch stock details
                stock = Stock.objects.get(pk=stock_id)
                stock_price = self.get_current_stock_price(stock.symbol)
                total_cost = stock_price * quantity

                # Fetch user's account
                custody_account = self.account_service.get_account(account_id)
                if not custody_account:
                    raise ValidationError(f"Account {str(account_id)} not found.")

                checking_account = self.account_service.get_account(custody_account.reference_account_id)
                if not checking_account:
                    raise ValidationError(f"Account {str(account_id)} not found.")

                bank_custody_account = self.account_service.get_bank_custody_account()
                if not bank_custody_account:
                    raise ValidationError(f"Bank custody account not found.")

                try:
                    self.account_service.validate_accounts_for_transaction(total_cost, checking_account.account_id, bank_custody_account.reference_account_id)
                except Exception as e:
                    raise ValidationError(f"Validation failed: {str(e)}.")

                bank_ownership = StockOwnership.objects.select_for_update().filter(
                    account=bank_custody_account, stock=stock
                ).first()

                if not bank_ownership or bank_ownership.quantity < quantity:
                    raise ValidationError(f"Insufficient stock quantity in the bank custody account: {bank_custody_account}.")

                if not self.transaction_service.create_new_stock_transaction(total_cost, checking_account.account_id, bank_custody_account.reference_account_id, stock_id, quantity, "buy"):
                    raise ValidationError("Transaction creation failed.")

                # Deduct stock from bank's account
                bank_ownership.quantity -= quantity
                bank_ownership.save()

                # Update stock ownership
                ownership, created = StockOwnership.objects.get_or_create(account=custody_account, stock=stock)
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
                stock_price = self.get_current_stock_price(stock.symbol)
                total_revenue = stock_price * quantity

                # Fetch stock ownership
                ownership = self.get_user_owned_stock(account_id, stock_id)
                if ownership.quantity < quantity:
                    raise ValidationError("Not enough stock to sell.")

                # Fetch user's account
                custody_account = self.account_service.get_account(account_id)
                if not custody_account:
                    raise ValidationError(f"Account {str(account_id)} not found.")

                checking_account = self.account_service.get_account(custody_account.reference_account_id)
                if not checking_account:
                    raise ValidationError(f"Account {str(account_id)} not found.")

                bank_custody_account = self.account_service.get_bank_custody_account()
                if not bank_custody_account:
                    raise ValidationError(f"Bank custody account not found.")

                try:
                    self.account_service.validate_accounts_for_transaction(total_revenue, bank_custody_account.reference_account_id, checking_account.account_id)
                except Exception as e:
                    raise ValidationError(f"Validation failed: {str(e)}.")

                bank_ownership, created = StockOwnership.objects.get_or_create(account=bank_custody_account, stock=stock)

                if not self.transaction_service.create_new_stock_transaction(total_revenue, bank_custody_account.reference_account_id, checking_account.account_id, stock_id, quantity, "sell"):
                    raise ValidationError("Transaction creation failed.")

                # Add stock to bank's account
                bank_ownership.quantity += quantity
                bank_ownership.save()

                # Reduce stock quantity
                ownership.quantity -= quantity
                if ownership.quantity == 0:
                    ownership.delete()
                else:
                    ownership.save()

            return True

        except Exception as e:
            raise ValidationError(f"Stock sale failed: {str(e)}")

    def get_current_stock_price(self, stock_symbol: str) -> float:
        try:
            # Fetch the stock object using `select_for_update` to lock the row for updates
            with transaction.atomic():
                stock = Stock.objects.select_for_update().filter(symbol=stock_symbol).first()
                if not stock:
                    raise ValidationError(f"Stock with symbol {stock_symbol} does not exist.")

                # Check if the `last_updated` is older than 1 minute
                if not stock.last_updated or (now() - stock.last_updated) > timedelta(minutes=1):
                    # Fetch the latest stock price
                    current_stock_price = fetch_stock_price(stock_symbol)

                    # Update the stock's current price and `last_updated` timestamp
                    stock.current_price = current_stock_price
                    stock.last_updated = now()
                    stock.save(update_fields=["current_price", "last_updated"])

                # Return the (possibly updated) current stock price
                return float(stock.current_price)
        except Exception as e:
            raise ValidationError(f"Failed to fetch and update stock price for {stock_symbol}: {str(e)}")