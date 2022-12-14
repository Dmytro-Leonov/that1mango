# Generated by Django 4.0.5 on 2022-06-16 15:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('title', '0021_alter_teamparticipant_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='teamparticipant',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='teamparticipant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='teamparticipant',
            unique_together={('user', 'team')},
        ),
    ]
