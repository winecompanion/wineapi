# Generated by Django 2.2.3 on 2019-10-14 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20191006_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='reservation',
            name='status',
            field=models.IntegerField(choices=[(1, 'Created'), (2, 'Confirmed'), (3, 'Rejected'), (4, 'Cancelled'), (5, 'Paid Out')], default=2),
        ),
        migrations.AlterField(
            model_name='eventoccurrence',
            name='vacancies',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='imagesevent',
            name='filefield',
            field=models.FileField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='imageswinery',
            name='filefield',
            field=models.FileField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='observations',
            field=models.TextField(blank=True),
        ),
    ]
