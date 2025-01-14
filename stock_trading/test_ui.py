from unittest.mock import patch, MagicMock
from dependency_injector import containers, providers
from django.urls import reverse
from django.test import TestCase
from marshmallow.exceptions import ValidationError
from uuid import uuid4

from core.services import ITradingService
from stock_trading.models import StockOwnership


class TestContainer(containers.DeclarativeContainer):
    trading_service = providers.Singleton(
        MagicMock,
        spec=ITradingService
    )

    stock_ownership = providers.Factory(
        MagicMock,
        spec=StockOwnership
    )


class StockTradingViewsTest(TestCase):

    def setUp(self):
        self.container = TestContainer()
        self.account_id = uuid4()

        # TODO : figure out how to display the stocks -> i've got error with no Bank Custody account was found

    def test_stock_market_view_no_account(self):

        with patch("stock_trading.views.AccountBase.objects.filter", return_value=MagicMock(first=MagicMock(return_value=None))):
            with self.assertRaises(ValidationError) as context:
                self.client.get(reverse("stock_trading:stock_market", args=[self.account_id]))

            self.assertEqual(str(context.exception), "No account found.")

    def test_buy_stock_get_request(self):

        response = self.client.get(reverse("stock_trading:buy_stock", args=[self.account_id]))

        self.assertEqual(response.status_code, 200)


        self.assertTemplateUsed(response, "stock_trading/buy_stock.html")

        self.assertIn("form", response.context)
        self.assertEqual(response.context["account_id"], self.account_id)

    def test_buy_stock_post_invalid_form(self):
        form_data = {"stock": "", "quantity": "invalid"}


        with patch("stock_trading.views.BuyStockForm.is_valid", return_value=False):
            response = self.client.post(reverse("stock_trading:buy_stock", args=[self.account_id]), data=form_data)

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "stock_trading/buy_stock.html")

            self.assertIn("form", response.context)
            self.assertFalse(response.context["form"].is_valid())


            self.container.trading_service().buy_stock.assert_not_called()
