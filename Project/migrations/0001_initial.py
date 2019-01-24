# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-12-17 12:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('filename', models.CharField(default=b'', max_length=128)),
                ('content', models.CharField(default=b'', max_length=250)),
                ('type', models.CharField(max_length=128)),
                ('createDate', models.DateTimeField(default=b'')),
                ('src', models.URLField(default=b'')),
            ],
        ),
        migrations.CreateModel(
            name='File_User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('time', models.IntegerField(default=1)),
                ('filename', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Project.File')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Token', models.CharField(max_length=250)),
                ('createDate', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=128)),
                ('password', models.CharField(max_length=250)),
                ('authTime', models.IntegerField(default=0)),
                ('createDate', models.DateTimeField(default=b'')),
                ('email', models.EmailField(default=b'', max_length=254)),
                ('isManager', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='token',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Project.User'),
        ),
        migrations.AddField(
            model_name='file_user',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Project.User'),
        ),
    ]
