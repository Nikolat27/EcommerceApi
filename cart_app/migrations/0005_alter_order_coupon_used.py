# Generated by Django 5.1.1 on 2024-10-04 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0004_alter_order_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='coupon_used',
            field=models.BooleanField(default=False),
        ),
    ]