# Generated by Django 2.2.3 on 2019-10-20 17:28

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20191014_1110'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=15)),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326, verbose_name='longitude/latitude'),
        ),
        migrations.CreateModel(
            name='BusinessHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_from', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')])),
                ('day_to', models.IntegerField(blank=True, choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], null=True)),
                ('hour_from', models.TimeField()),
                ('hour_to', models.TimeField()),
                ('aditional_from', models.TimeField(blank=True, null=True)),
                ('aditional_to', models.TimeField(blank=True, null=True)),
                ('restaurant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_hours', to='api.Event')),
                ('winery', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_hours', to='api.Winery')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='contact',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.ContactInfo'),
        ),
        migrations.AddField(
            model_name='winery',
            name='contact',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.ContactInfo'),
        ),
    ]
