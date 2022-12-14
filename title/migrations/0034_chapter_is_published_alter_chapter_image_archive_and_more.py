# Generated by Django 4.0.5 on 2022-07-03 14:03

from django.db import migrations, models
import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0033_chapter_image_archive'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='is_published',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='chapter',
            name='image_archive',
            field=models.FileField(null=True, upload_to='titles/chapters', verbose_name='archive with chapter pages'),
        ),
        migrations.AlterField(
            model_name='teamparticipant',
            name='roles',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(choices=[('admin', 'Админ'), ('translator', 'Переводчик'), ('cleaner', 'Клинер'), ('typesetter', 'Тайпер'), ('editor', 'Эдитор'), ('corrector', 'Корректор'), ('beta_reader', 'Бета читатель'), ('scanner', 'Сканер'), ('uploader', 'Загрузчик')], max_length=11), blank=True, null=True, size=None),
        ),
    ]
