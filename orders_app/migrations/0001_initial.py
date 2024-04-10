# Generated by Django 5.0.3 on 2024-04-09 17:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cart_app', '0003_cart_subtotal'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, max_length=120)),
                ('status', models.CharField(default='created', max_length=120)),
                ('shipping_total', models.DecimalField(decimal_places=2, default=9.99, max_digits=20)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart_app.cart')),
            ],
        ),
    ]