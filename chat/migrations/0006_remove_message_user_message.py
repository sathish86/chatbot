# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2018-04-25 07:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_auto_20180425_0735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='user_message',
        ),
    ]