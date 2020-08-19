# Generated by Django 3.0.7 on 2020-07-22 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20200722_1335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='Person_Name',
        ),
        migrations.AddField(
            model_name='person',
            name='abbreviated_first_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='abbreviated_last_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='alt_spelling_first_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='alt_spelling_last_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='first_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='last_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Person_Name',
        ),
    ]
