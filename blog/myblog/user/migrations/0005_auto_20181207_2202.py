# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-07 14:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20181207_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='age',
            field=models.IntegerField(default=18),
        ),
    ]
