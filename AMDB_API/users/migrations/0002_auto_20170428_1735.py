# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-28 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='users',
            name='updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
