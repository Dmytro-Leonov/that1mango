# Generated by Django 4.0.5 on 2022-06-23 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0017_comment_dislikes_alter_comment_likes'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='commentvote',
            unique_together=set(),
        ),
    ]
