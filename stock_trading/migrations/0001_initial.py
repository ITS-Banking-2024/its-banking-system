# Generated by Django 4.2 on 2025-01-17 14:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.ACCOUNT_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Stock",
            fields=[
                (
                    "stockID",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("stock_name", models.CharField(max_length=200)),
                ("current_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("symbol", models.CharField(max_length=10)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "stock",
            },
        ),
        migrations.CreateModel(
            name="StockOwnership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=0)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="account",
                        to=settings.ACCOUNT_MODEL,
                    ),
                ),
                (
                    "stock",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="stock",
                        to="stock_trading.stock",
                    ),
                ),
            ],
            options={
                "db_table": "stock_ownership",
                "unique_together": {("account", "stock")},
            },
        ),
    ]
