# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('filename', models.CharField(default=b'', max_length=128)),
                ('content', models.CharField(default=b'', max_length=250)),
                ('type', models.CharField(max_length=128)),
                ('createDate', models.DateTimeField(default=b'')),
                ('src', models.URLField(default=b'')),
                ('group', models.CharField(default=b'', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='File_User',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('time', models.DecimalField(max_digits=10, decimal_places=2)),
                ('filename', models.ForeignKey(to='Project.File')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Token', models.CharField(max_length=250)),
                ('createDate', models.DateTimeField()),
                ('expires', models.DecimalField(max_digits=20, decimal_places=9)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('username', models.CharField(max_length=128)),
                ('password', models.CharField(max_length=250)),
                ('authTime', models.IntegerField(default=0)),
                ('createDate', models.DateTimeField(default=b'')),
                ('email', models.EmailField(default=b'', max_length=254)),
                ('isManager', models.BooleanField(default=False)),
                ('group', models.CharField(default=b'', max_length=250)),
            ],
        ),
        migrations.AddField(
            model_name='token',
            name='username',
            field=models.ForeignKey(to='Project.User'),
        ),
        migrations.AddField(
            model_name='file_user',
            name='username',
            field=models.ForeignKey(to='Project.User'),
        ),
    ]
