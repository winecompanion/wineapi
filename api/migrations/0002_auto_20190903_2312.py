# Generated by Django 2.2.3 on 2019-09-03 23:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='canceled',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='winery',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='api.Winery'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='eventoccurrence',
            name='end',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='eventoccurrence',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='occurrences', to='api.Event'),
        ),
        migrations.AlterField(
            model_name='eventoccurrence',
            name='start',
            field=models.DateTimeField(),
        ),
    ]