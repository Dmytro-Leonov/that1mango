from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('title', '0001_initial'),
        ('social', '0002_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('social', '0002_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('title', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=30, unique=True, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='username')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('profile_pic', models.ImageField(blank=True, upload_to='profile_pictures/%Y/%m', verbose_name='profile picture')),
                ('about', models.TextField(blank=True, max_length=200, verbose_name='about')),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('comments', models.ManyToManyField(related_name='users_of_comment', through='social.CommentVote', to='social.comment', verbose_name='comments')),
                ('friends', models.ManyToManyField(related_name='users_of_friend', through='social.Friend', to=settings.AUTH_USER_MODEL, verbose_name='friends with')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('subscriptions', models.ManyToManyField(related_name='subscribed_users', to='title.title', verbose_name='subscriptions')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
