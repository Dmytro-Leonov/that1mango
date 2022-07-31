# Generated by Django 4.0.5 on 2022-06-11 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0011_publisher_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='description',
        ),
        migrations.AlterField(
            model_name='person',
            name='picture',
            field=models.ImageField(blank=True, upload_to='persons/pictures/%Y', verbose_name='Person picture'),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='picture',
            field=models.ImageField(blank=True, upload_to='publishers/pictures/%Y', verbose_name='Publisher picture'),
        ),
    ]
