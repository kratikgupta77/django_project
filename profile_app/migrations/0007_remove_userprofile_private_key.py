# Generated by Django 5.1.6 on 2025-03-24 19:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile_app', '0006_rename_content_message_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='private_key',
        ),
    ]
