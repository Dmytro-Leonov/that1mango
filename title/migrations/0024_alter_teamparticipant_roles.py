# Generated by Django 4.0.5 on 2022-06-16 16:43

from django.db import migrations, models
import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0023_remove_teamparticipant_role_teamparticipant_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamparticipant',
            name='roles',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(choices=[('translator ', 'Переводчик'), ('cleaner', 'Клинер'), ('typesetter', 'Тайпер'), ('editor', 'Эдитор'), ('corrector', 'Корректор'), ('beta_reader', 'Бета читатель'), ('scanner', 'Сканер'), ('admin', 'Админ')], max_length=11), blank=True, null=True, size=None),
        ),
    ]
