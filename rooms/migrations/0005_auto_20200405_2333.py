# Generated by Django 2.2.5 on 2020-04-05 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_auto_20200405_0335'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='descriptiom',
            new_name='description',
        ),
    ]