# Generated by Django 5.0.3 on 2024-04-07 01:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products_app', '0008_product_slug_name'),
        ('tags_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tags',
            new_name='Tag',
        ),
    ]