# Generated by Django 5.0.3 on 2024-04-02 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=39.99, max_digits=10),
        ),
    ]
