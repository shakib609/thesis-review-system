# Generated by Django 2.0.5 on 2018-05-21 21:47

from django.db import migrations
import website.registration.models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', website.registration.models.CutomUserManager()),
            ],
        ),
    ]