# Generated by Django 2.0.5 on 2018-05-23 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('thesis', '0001_initial'),
        ('registration', '0002_auto_20180522_0347'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='studentgroup',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='thesis.StudentGroup'),
        ),
    ]