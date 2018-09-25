# Generated by Django 2.1 on 2018-09-25 17:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('thesis', '0008_studentgroup_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('teachers', models.ManyToManyField(related_name='fields', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='studentgroup',
            name='field',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='studentgroups', to='thesis.ResearchField'),
        ),
    ]
