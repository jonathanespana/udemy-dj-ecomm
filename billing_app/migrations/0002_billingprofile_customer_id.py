# Generated by Django 5.0.3 on 2024-04-18 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingprofile',
            name='customer_id',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
