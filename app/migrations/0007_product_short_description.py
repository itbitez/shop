# Generated by Django 5.1 on 2024-09-12 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_product_sku'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='short_description',
            field=models.TextField(default=2),
            preserve_default=False,
        ),
    ]
