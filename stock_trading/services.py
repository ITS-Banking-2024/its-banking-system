from decimal import Decimal
from uuid import UUID
from django.db import transaction
from marshmallow import ValidationError
import requests

from core.services import ITradingService
from stock_trading.models import Stock, StockOwnership


class TradingService(ITradingService):
    STOCK_PRICE_API_URL = ""

    def __init__(self, transaction_service, stock_manager):
        self.transaction_service = transaction_service
        self.stock_manager = stock_manager

    def fetch_stock_price(self, stock_id: UUID) -> Decimal:
        response = requests.get(f"{self.STOCK_PRICE_API_URL}/{stock_id}")
        if response.status_code != 200:
            raise ValidationError("Failed to fetch stock price.")
        return Decimal(response.json()["price"])

    def buy_stock(self, account_id: UUID, stock_id: UUID, quantity: int) -> bool:
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")

        try:
            with transaction.atomic():
                # Fetch stock price
                stock_price = self.fetch_stock_price(stock_id)
                total_cost = stock_price * Decimal(quantity)

                # Fetch user's account
                account = CheckingAccount.objects.filter(account_id=account_id).first()
                if not account:
                    raise ValidationError("Account not found.")



                # Deduct cost from the account
                self.transaction_service.create_new_transaction(
                    amount=total_cost,
                    sending_account_id=account_id,
                    receiving_account_id=None,  # Bank/stock market account can be abstracted
                )

                # Update stock ownership
                stock, _ = Stock.objects.get_or_create(pk=stock_id)
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
                # Fetch stock price
                stock_price = self.fetch_stock_price(stock_id)
                total_revenue = stock_price * Decimal(quantity)

                # Fetch stock ownership
                ownership = StockOwnership.objects.filter(account_id=account_id, stock_id=stock_id).first()
                if not ownership or ownership.quantity < quantity:
                    raise ValidationError("Not enough stock to sell.")

                # Reduce stock quantity
                ownership.quantity -= quantity
                ownership.save()

                # Credit revenue to the account
                self.transaction_service.create_new_transaction(
                    amount=total_revenue,
                    sending_account_id=None,  # Bank/stock market account can be abstracted
                    receiving_account_id=account_id,
                )

            return True

        except Exception as e:
            raise ValidationError(f"Stock sale failed: {str(e)}")

    def get_current_stock_price(self, stock_id: UUID) -> float:
        return float(self.fetch_stock_price(stock_id))
