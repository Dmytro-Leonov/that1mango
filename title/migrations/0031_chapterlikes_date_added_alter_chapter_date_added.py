# Generated by Django 4.0.5 on 2022-06-24 17:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0030_alter_title_title_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapterlikes',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='chapter',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
