# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-04 13:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0004_auto_20171113_0958'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='AbstractUser',
        ),
    ]
