# Generated by Django 4.0.5 on 2022-06-24 14:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social', '0018_alter_commentvote_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.TextField(max_length=1500, verbose_name='comment'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments_of_user', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('new_chapter', 'Вышла новая глава'), ('status_changed', 'У тайтла изменился статус'), ('friend_request', 'Новый апрос в друзья'), ('friend_accepted', 'Пользователь подтвердил ваш запрос на дружбу'), ('join_team_request', 'Вас пригласили вступить в команду переводчиков'), ('team_kick', 'Вас исключили из команды переводчиков'), ('comment_reply', 'Пользователь дал ответ на ваш комментарий')], max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='commentvote',
            unique_together={('user', 'comment', 'vote')},
        ),
    ]
