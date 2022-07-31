# Generated by Django 4.0.5 on 2022-07-01 15:23

from django.db import migrations, models
import django.db.models.deletion
import title.models


class Migration(migrations.Migration):

    dependencies = [
        ('title', '0031_chapterlikes_date_added_alter_chapter_date_added'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChapterImages',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('image', title.models.CloudinaryImage(max_length=255)),
                ('chapter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images_of_chapter', to='title.chapter')),
            ],
        ),
    ]
