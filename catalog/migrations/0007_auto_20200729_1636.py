# Generated by Django 3.0.7 on 2020-07-29 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_auto_20200729_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='date_of_death',
            field=models.DateField(blank=True, null=True),
        ),
    ]
