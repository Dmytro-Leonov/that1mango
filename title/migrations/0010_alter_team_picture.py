# Generated by Django 4.0.5 on 2022-06-10 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0009_alter_team_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='picture',
            field=models.ImageField(blank=True, upload_to='teams/pictures/%Y', verbose_name='Team picture'),
        ),
    ]
