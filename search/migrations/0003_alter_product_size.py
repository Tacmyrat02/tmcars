# Generated by Django 5.1.1 on 2024-10-13 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_alter_product_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='size',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
