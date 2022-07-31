from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('title', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertitlerating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='titlerating',
            name='rating',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='title.rating'),
        ),
        migrations.AddField(
            model_name='titlerating',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings_of_title', to='title.title'),
        ),
        migrations.AddField(
            model_name='titleperson',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='title.person'),
        ),
        migrations.AddField(
            model_name='titleperson',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='title.title'),
        ),
        migrations.AddField(
            model_name='title',
            name='keyword',
            field=models.ManyToManyField(related_name='titles_of_keyword', to='title.keyword', verbose_name='title keyword'),
        ),
        migrations.AddField(
            model_name='title',
            name='person',
            field=models.ManyToManyField(related_name='titles_of_person', through='title.TitlePerson', to='title.person', verbose_name='title person'),
        ),
        migrations.AddField(
            model_name='title',
            name='publisher',
            field=models.ManyToManyField(related_name='titles_of_publisher', to='title.publisher', verbose_name='title publisher'),
        ),
        migrations.AddField(
            model_name='title',
            name='release_format',
            field=models.ManyToManyField(related_name='titles_with_release_format', to='title.releaseformat', verbose_name='release formats'),
        ),
        migrations.AddField(
            model_name='title',
            name='title_rating',
            field=models.ManyToManyField(related_name='titles_with_rating', through='title.TitleRating', to='title.rating', verbose_name='title rating'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='title.title'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='usertitlerating',
            unique_together={('user', 'title', 'rating')},
        ),
        migrations.AlterUniqueTogether(
            name='titlerating',
            unique_together={('title', 'rating')},
        ),
        migrations.AlterUniqueTogether(
            name='titleperson',
            unique_together={('title', 'person', 'title_role')},
        ),
    ]
