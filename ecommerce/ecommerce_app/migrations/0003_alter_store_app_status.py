# Generated by Django 3.2.12 on 2024-03-20 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_app', '0002_auto_20240320_1924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='app_status',
            field=models.CharField(choices=[('active', 'Active'), ('deactive', 'Deactive')], max_length=100),
        ),
    ]
