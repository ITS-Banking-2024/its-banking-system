from typing import Optional, List, Union

from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet
from core.managers import CoreProductManager
from core.models import Customer

from django.contrib.auth.base_user import BaseUserManager


class CustomerManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email for user must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

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