# Generated by Django 3.0.7 on 2020-07-28 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0007_auto_20200725_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cgpa',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]