# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-23 03:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OptionTransData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_date', models.DateField(verbose_name='trans_date')),
                ('strike_price', models.PositiveIntegerField(default=0, verbose_name='strike_price')),
                ('expiration_date', models.CharField(default='', max_length=8, verbose_name='expiration_date')),
                ('classification', models.CharField(choices=[('1', 'C'), ('2', 'P')], default=1, max_length=1, verbose_name='classification')),
                ('trans_time', models.TimeField(verbose_name='trans_time')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='price')),
                ('volume', models.PositiveIntegerField(default=0, verbose_name='volume')),
            ],
        ),
        migrations.CreateModel(
            name='Trading_Date',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trading_date', models.DateField(unique=True, verbose_name='trading_date')),
                ('day_of_week', models.PositiveIntegerField(default=9, verbose_name='day_of_week')),
                ('is_future_delivery_day', models.BooleanField(default=False, verbose_name='is_future_delivery_day')),
                ('first_trading_day_of_month', models.BooleanField(default=False, verbose_name='first_trading_day_of_month')),
                ('last_trading_day_of_month', models.BooleanField(default=False, verbose_name='last_trading_day_of_month')),
                ('is_market_closed', models.BooleanField(default=False, verbose_name='is_market_closed')),
            ],
        ),
    ]