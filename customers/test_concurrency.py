import threading

from django.db import transaction
from django.test import TransactionTestCase

from customers.models import Customer
from customers.services import CustomerService


# the django UnitTest would inherit from TransactionTestCase, but it does too much stuff resulting in database locks
class CustomerServiceConcurrencyTestCase(TransactionTestCase):
    def setUp(self):
        super().setUp()
        self._is_test_running = True
        with transaction.atomic():
            self.customer = Customer.objects.create(pk=1, credit=100)
            self.customer.save()

        self.customer_service = CustomerService()

    def _redeem_credit_concurrently(self, amount, success_counter, exception_counter):
        try:
            result = self.customer_service.redeem_credit(self.customer, amount)
            success_counter.increment()
        except Exception:
            exception_counter.increment()
        return

    def test_redeem_credit_concurrency(self):

        success_counter = Counter()
        exception_counter = Counter()

        # Set the number of concurrent threads
        num_threads = 10
        redeem_value = 10

        # Create and start the concurrent threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=self._redeem_credit_concurrently,
                                      args=(redeem_value, success_counter, exception_counter))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Assert that the credit redemption is correct after concurrent attempts
        expected_credit = 100 - (success_counter.value*redeem_value)
        expected_exceptions = num_threads - success_counter.value
        print(f"number of exceptions: {str(exception_counter.value)} and number of successes: "
              f"{str(success_counter.value)} with expected credit: {str(expected_credit)}")

        # we must reload the customer from the database, because self.customer is not updated
        # (yet another django ORM flaw)
        self.assertEqual(Customer.objects.get().credit, expected_credit)
        self.assertEqual(exception_counter.value, expected_exceptions)
        # we expect that at least one exception was raised
        self.assertGreater(exception_counter.value, 0)


class Counter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._value += 1

    @property
    def value(self):
        with self._lock:
            return self._value
