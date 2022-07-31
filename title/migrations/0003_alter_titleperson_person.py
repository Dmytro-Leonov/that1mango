# Generated by Django 4.0.4 on 2022-06-08 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titleperson',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='persons_of_title', to='title.person'),
        ),
    ]
