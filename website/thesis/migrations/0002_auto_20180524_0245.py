# Generated by Django 2.0.5 on 2018-05-23 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesis', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentgroup',
            name='md5hash',
            field=models.CharField(max_length=10, null=True),
        ),
    ]