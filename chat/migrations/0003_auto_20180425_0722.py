# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2018-04-25 07:22
from __future__ import unicode_literals

from django.db import migrations, models

def default_questions(apps, schema_editor):
    BotQuestions = apps.get_model("chat", "BotQuestions")
    list_question = [" Hello, I am going to ask you few questions that will help me know you better?",
    "What is your name?",
    "Are you male or female?",
    "When were you born?",
    "Are you a smoker?",
    "Thank you. Press 'Done' for results."]
    for ele in list_question:
        BotQuestions.objects.create(question=ele)
    

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20180425_0722'),
    ]

    operations = [
        migrations.RunPython(default_questions),
    ]
