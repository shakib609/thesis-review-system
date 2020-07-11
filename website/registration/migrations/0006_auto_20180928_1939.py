# Generated by Django 2.1 on 2018-09-28 13:39

from django.db import migrations, models
import website.registration.models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0005_auto_20180928_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cv_document',
            field=models.FileField(null=True, upload_to=website.registration.models.generate_cv_upload_location),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(null=True, upload_to=website.registration.models.generate_propic_upload_location),
        ),
    ]