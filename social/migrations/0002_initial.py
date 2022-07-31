from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('title', '0001_initial'),
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='chapter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='title.chapter'),
        ),
    ]
