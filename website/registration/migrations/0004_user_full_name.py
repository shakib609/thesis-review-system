# Generated by Django 2.1 on 2018-09-28 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_user_studentgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='full_name',
            field=models.CharField(default='Temporary Full Name', max_length=180, verbose_name='full name'),
            preserve_default=False,
        ),
    ]