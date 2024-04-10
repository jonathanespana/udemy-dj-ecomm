# Generated by Django 5.0.3 on 2024-04-08 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0002_cart_created_at_cart_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
    ]