# Generated by Django 5.1.6 on 2025-04-03 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile_app', '0010_groupmessage_media_message_media'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='media',
            field=models.FileField(blank=True, null=True, upload_to='uploads/'),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
