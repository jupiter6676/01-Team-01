# Generated by Django 3.2.13 on 2022-11-06 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_auto_20221104_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='articles',
            name='view_count',
            field=models.IntegerField(default=0),
        ),
    ]
