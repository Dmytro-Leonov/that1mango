# Generated by Django 4.0.5 on 2022-07-04 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0035_alter_chapter_options_alter_chapter_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='title',
            name='chapters',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]