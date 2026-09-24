from django.db import migrations

from common.rls import enable_rls


class Migration(migrations.Migration):
    """Each firm's trade network, blasts, replies and inbox are private to that firm."""

    dependencies = [("trade", "0001_initial")]

    operations = [
        enable_rls("trade_fellowbroker"),
        enable_rls("trade_tradeblast"),
        enable_rls("trade_tradereply"),
        enable_rls("trade_tradedelivery"),
    ]
