# Generated by Django 5.1.1 on 2024-09-25 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_alter_orderitem_product_alter_orderitem_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.CharField(max_length=100),
        ),
    ]
