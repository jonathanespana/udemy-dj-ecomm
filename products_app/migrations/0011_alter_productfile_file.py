# Generated by Django 5.0.3 on 2024-05-16 16:16

import django.core.files.storage
import products_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products_app', '0010_productfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productfile',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='//dj-ecommerce-app.s3.amazonaws.com/protected_media/'), upload_to=products_app.models.upload_product_file_loc),
        ),
    ]
