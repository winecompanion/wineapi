# Generated by Django 2.2.3 on 2019-09-14 22:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20190914_2201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventcategory',
            old_name='category_name',
            new_name='name',
        ),
    ]