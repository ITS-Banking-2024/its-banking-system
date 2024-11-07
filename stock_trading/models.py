from core.models import Stock as AbstractStock
from django.db import models

class Stock(AbstractStock):  # Concrete implementation, uses the same name
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stock"
