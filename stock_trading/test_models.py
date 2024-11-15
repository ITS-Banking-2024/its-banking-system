from django.test import TestCase
from stock_trading.models import Stock

class StockModelTest(TestCase):
    def setUp(self):
        pass


    def test_get_by_stock_name(self):

        # create a new Stock object
        stock = Stock.objects.create(stock_name='AAPL', current_price=150.00, stockID='123e4567-e89b-12d3-a456-426614174000')

        # query for the Stock object by stock_name
        stock_query = Stock.objects.get_by_stock_name('AAPL')

        # check that the Stock object was retrieved successfully
        self.assertEqual(stock_query.first(), stock)

    def test_get_by_stock_id(self):

        # create a new Stock object
        stock = Stock.objects.create(stock_name='AAPL', current_price=150.00, stockID='123e4567-e89b-12d3-a456-426614174000')

        # query for the Stock object by stock_id
        stock_query = Stock.objects.get_by_stock_id('123e4567-e89b-12d3-a456-426614174000')

        # check that the Stock object was retrieved successfully
        self.assertEqual(stock_query.first(), stock)


    def test_get_all_stocks(self):

            # create a new Stock object
            stock = Stock.objects.create(stock_name='AAPL', current_price=150.00, stockID='123e4567-e89b-12d3-a456-426614174000')
            stock_2 = Stock.objects.create(stock_name='GOOGL', current_price=2500.00, stockID='123e4567-e89b-12d3-a456-426614174001')

            # query for all Stock objects
            stock_query = Stock.objects.get_all_stocks()

            # check that the Stock object was retrieved successfully
            self.assertEqual(len(stock_query), 2)