# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2018-04-25 07:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_auto_20180425_0731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='user_message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messaged_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
