# Generated by Django 4.0.5 on 2022-07-19 13:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='birth_date',
            field=models.DateField(default=datetime.datetime(2022, 7, 19, 16, 33, 9, 865713)),
            preserve_default=False,
        ),
    ]
