from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

from core.managers import CoreProductManager


# Create your models here.
# we define an abstract class Product here, so that we can use different types of products later
class Product(models.Model):
    # Use custom manager to inherit the queryset methods from the CoreProductManager
    objects = CoreProductManager()

    # Make this class abstract to prevent it from being instantiated directly as it serves as an interface
    class Meta:
        abstract = True

    # each product has a name and a description
    name: str = models.CharField(max_length=200)
    description: str = models.TextField()

    def __str__(self) -> str:
        return self.name


"""
In Django, the AbstractUser class is a built-in model class that provides a starting point for creating a
custom user model. It is designed to be subclassed by users who wish to implement their own custom user model while 
retaining some of the core functionality of the built-in Django User model.
By inheriting from AbstractUser, the Customer model class is able to inherit the fields and methods 
of the AbstractUser class, which includes built-in user authentication and authorization features, 
such as the ability to log in, log out, and set a password. 
This allows developers to easily customize the user model to fit their specific needs while still retaining 
the core functionality of the built-in user model.
"""


class Customer(AbstractUser):
    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.username

class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    address = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self.user_id}, {self.first_name}, {self.last_name}'


class Account(models.Model):
    account_id = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    user_id = models.ForeignKey(User, related_name='accounts', on_delete=models.CASCADE)

    class Meta:
        abstract = True
