# Generated by Django 4.0.5 on 2022-06-18 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0026_alter_teamparticipant_roles_alter_titleteam_team'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'ordering': ['-volume_number', '-chapter_number']},
        ),
    ]
