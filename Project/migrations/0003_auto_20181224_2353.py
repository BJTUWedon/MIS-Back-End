# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-12-24 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0002_token_expires'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file_user',
            name='time',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='token',
            name='expires',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
