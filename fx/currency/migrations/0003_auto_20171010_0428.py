# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-10 04:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0002_auto_20171010_0424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rate',
            name='cash_buying',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='rate',
            name='cash_selling',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='rate',
            name='spot_buying',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='rate',
            name='spot_selling',
            field=models.FloatField(null=True),
        ),
    ]
