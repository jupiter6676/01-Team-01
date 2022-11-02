# Generated by Django 3.2.13 on 2022-11-02 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_auto_20221101_1634'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_content', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='tagging',
            field=models.ManyToManyField(related_name='tagged', to='articles.Tag'),
        ),
    ]
