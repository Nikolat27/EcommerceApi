# Generated by Django 5.1.1 on 2024-10-04 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0006_reserve'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='is_enable',
            field=models.BooleanField(default=True),
        ),
    ]
