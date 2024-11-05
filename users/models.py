from django.db import models

from core.models import User

class UserBase(User):
    class Meta:
        db_table: str = "user_base"

class User(UserBase):
    class Meta:
        db_table: str = "user"
