# Generated by Django 3.0.8 on 2020-07-04 04:08

from django.db import migrations

from users.models import RoleType


def create_default_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    for _, name in RoleType.choices:
        Role.objects.create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_roles),
    ]
