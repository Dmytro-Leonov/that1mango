# Generated by Django 4.0.5 on 2022-06-10 14:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0008_alter_teamparticipant_role_and_more'),
        ('social', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='title.team'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('new_chapter', 'Вышла новая глава'), ('status_changed', 'У тайтла изменился статус'), ('friend_request', 'Новый апрос в друзья'), ('friend_accepted', 'Пользователь подтвердил запрос на дружбу'), ('join_team_request', 'Вас пригласили вступить в команду переводчиков')], max_length=20),
        ),
    ]