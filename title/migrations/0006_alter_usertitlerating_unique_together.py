# Generated by Django 4.0.5 on 2022-06-10 12:36

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('title', '0005_rename_teamparticipants_teamparticipant'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usertitlerating',
            unique_together={('user', 'title')},
        ),
    ]
