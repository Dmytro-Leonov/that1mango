# Generated by Django 4.0.5 on 2022-06-11 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0004_notification_team_alter_notification_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('new_chapter', 'Вышла новая глава'), ('status_changed', 'У тайтла изменился статус'), ('friend_request', 'Новый апрос в друзья'), ('friend_accepted', 'Пользователь подтвердил запрос на дружбу'), ('join_team_request', 'Вас пригласили вступить в команду переводчиков'), ('comment_reply', 'Пользователь дал ответ на ваш комментарий')], max_length=20),
        ),
    ]