# Create your models here.
from django.contrib.auth.models import AbstractUser
from customers.managers import CustomerManager

from core.models import Customer

"""
    we are using the Customer model for authentication, so we need to use the AbstractUser model
    for this project, only add nullable fields to the customer,
    otherwise you could run into trouble with creating suerpusers.

"""


class CustomerBase(Customer):

    objects: CustomerManager = CustomerManager()

    class Meta:
        # swappable is used to swap out the default user model with our custom user model
        swappable: str = "CUSTOMER_MODEL"
        db_table: str = "customer_base"



# this is the concrete model that we will use for the project
class Customer(CustomerBase):
    class Meta:
        db_table: str = "customer_concrete"
