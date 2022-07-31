import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='chapter name')),
                ('volume', models.PositiveSmallIntegerField(unique=True)),
                ('chapter', models.FloatField(unique=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('-chapter', 'volume'),
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='keyword name')),
                ('slug', models.SlugField(unique=True)),
                ('type', models.CharField(choices=[('Genre', 'Жанр'), ('Tag', 'Тег')], default='Genre', max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='person name')),
                ('alternative_names', django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(max_length=200, unique=True), blank=True, null=True, size=5, verbose_name='alternative names')),
                ('description', models.TextField(blank=True, max_length=1000, verbose_name='description')),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='publisher name')),
                ('slug', models.SlugField(unique=True)),
                ('alternative_names', django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(max_length=200, unique=True), blank=True, null=True, size=5, verbose_name='alternative names')),
                ('description', models.TextField(blank=True, max_length=1000, verbose_name='description')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('mark', models.PositiveSmallIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(10)])),
                ('description', models.CharField(max_length=50, unique=True, verbose_name='description')),
            ],
            options={
                'ordering': ('-mark',),
            },
        ),
        migrations.CreateModel(
            name='ReleaseFormat',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10, unique=True, verbose_name='Release format name')),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='title name')),
                ('slug', models.SlugField(unique=True)),
                ('english_name', models.CharField(max_length=200, unique=True, verbose_name='english name')),
                ('alternative_names', django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(max_length=200, unique=True), size=10, verbose_name='alternative names')),
                ('description', models.TextField(max_length=1500, verbose_name='description')),
                ('release_year', models.IntegerField(default=2022, validators=[django.core.validators.MinValueValidator(1900, 'Release year must be greater than 1900'), django.core.validators.MaxValueValidator(2022, 'Release year must be less than or equal to 2022')], verbose_name='release year')),
                ('poster', models.ImageField(upload_to='posters/%Y/%m', verbose_name='title poster')),
                ('chapter_count', models.PositiveIntegerField(blank=True, default=0, verbose_name='chapter count')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('age_rating', models.CharField(choices=[('E', 'Все возраста'), ('Y', '10+'), ('T', '13+'), ('OT', '16+'), ('M', '18+')], default='E', max_length=2)),
                ('title_type', models.CharField(choices=[('Manga', 'Манга'), ('Manhwa', 'Манхва'), ('Manhua', 'Маньхуа')], default='Manga', max_length=10)),
                ('title_status', models.CharField(choices=[('Announcement', 'Анонс'), ('Ongoing', 'Продолжается'), ('Finished', 'Завершен'), ('Suspended', 'Приостановлен'), ('Stopped', 'Выпуск прекращен')], default='Announcement', max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='TitlePerson',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title_role', models.CharField(choices=[('Author', 'Автор'), ('Artist', 'Художник')], max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='TitleRating',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.PositiveIntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserTitleRating',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('rating', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='title.rating')),
                ('title', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='title.title')),
            ],
        ),
    ]
