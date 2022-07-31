from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField(max_length=500, verbose_name='comment')),
                ('is_deleted', models.BooleanField(blank=True, default=False)),
                ('likes', models.PositiveIntegerField(blank=True, default=0, verbose_name='likes')),
            ],
        ),
        migrations.CreateModel(
            name='CommentVote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('vote', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=30, verbose_name='list name')),
                ('hidden', models.BooleanField(blank=True, default=False, verbose_name='hidden')),
                ('titles_count', models.IntegerField(blank=True, default=0, verbose_name='titles in list')),
            ],
        ),
        migrations.CreateModel(
            name='ListTitle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('add_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('new_chapter', 'Вышла новая глава'), ('status_changed', 'У тайтла изменился статус'), ('friend_request', 'Новый апрос в друзья'), ('friend_accepted', 'Пользователь подтвердил запрос на дружбу')], max_length=15)),
            ],
        ),
    ]
