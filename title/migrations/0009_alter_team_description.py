# Generated by Django 4.0.5 on 2022-06-10 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0008_alter_teamparticipant_role_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='description',
            field=models.TextField(max_length=300, unique=True, verbose_name='description'),
        ),
    ]
