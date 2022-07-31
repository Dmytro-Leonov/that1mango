# Generated by Django 4.0.5 on 2022-06-23 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0016_remove_comment_votes'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='dislikes',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='comment',
            name='likes',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]