# Generated by Django 2.2.3 on 2019-10-03 18:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_imageswinery'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImagesEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filefield', models.FileField(blank=True, null=True, upload_to='')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='api.Event')),
            ],
        ),
    ]