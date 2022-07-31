# Generated by Django 4.0.5 on 2022-06-19 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0029_alter_usertitlerating_user'),
        ('social', '0009_alter_list_name_alter_subscription_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listtitle',
            old_name='add_date',
            new_name='date_added',
        ),
        migrations.AlterField(
            model_name='list',
            name='titles_count',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='titles in list'),
        ),
        migrations.AlterField(
            model_name='listtitle',
            name='title',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lists_of_title', to='title.title'),
        ),
    ]
