# Generated by Django 2.0.5 on 2018-05-29 20:21

from django.db import migrations, models
import django.db.models.deletion
import website.thesis.models


class Migration(migrations.Migration):

    dependencies = [
        ('thesis', '0002_auto_20180524_0245'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload_time', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to=website.thesis.models.generate_upload_location)),
                ('studentgroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='thesis.StudentGroup')),
            ],
        ),
    ]