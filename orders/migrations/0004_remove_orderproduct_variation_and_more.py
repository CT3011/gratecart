# Generated by Django 4.2.2 on 2023-07-01 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_rename_cariation_category_variation_variation_category'),
        ('orders', '0003_remove_orderproduct_color_remove_orderproduct_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='variation',
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='variations',
            field=models.ManyToManyField(blank=True, to='store.variation'),
        ),
    ]
