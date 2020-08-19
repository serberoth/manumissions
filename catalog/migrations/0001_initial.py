# Generated by Django 3.0.7 on 2020-07-16 20:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Age_Freed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Age_Freed', models.CharField(help_text='Enter the age of the respective person at their freed date', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Age_Listed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Age_Listed', models.CharField(help_text='Enter the age  listed on the manumission of the respective person', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Birth_Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Birth_Place', models.CharField(help_text='Enter the Birth place of the respective person', max_length=200)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Death_Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Death_Place', models.CharField(help_text='Enter the Death Place of the respective person', max_length=200)),
                ('date_of_death', models.DateField(blank=True, null=True, verbose_name='died')),
            ],
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Gender', models.CharField(help_text='Enter the assumed gender of the respective person', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Image_name',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter the image/scan name for the manumission (e.g. HC10-1000X_XXX.)', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Monthly_Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Monthly_Meeting', models.CharField(help_text='Enter the Monthly Meeting listed on the manumission documents', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('alt_spelling_first_name', models.CharField(max_length=100)),
                ('alt_spelling_last_name', models.CharField(max_length=100)),
                ('abbreviated_first_name', models.CharField(max_length=100)),
                ('abbreviated_last_name', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Page_Number',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter the Page Numbe listed in the Physical manumission book for the respective manumission', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Place_Freed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Place_Freed', models.CharField(help_text='Enter the Place where their manumission took place', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Enter a person's role", max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Year_Manumitted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Year_Manumitted', models.CharField(help_text='Enter the Year of their freed date', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_Manumission_Signing', models.DateField(blank=True, null=True)),
                ('Age_Freed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Age_Freed')),
                ('Age_Listed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Age_Listed')),
                ('Birth_Place', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Birth_Place')),
                ('Death_Place', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Death_Place')),
                ('Gender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Gender')),
                ('Name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Name')),
                ('Place_Freed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Place_Freed')),
                ('Role', models.ManyToManyField(help_text='Select a role for this person', to='catalog.Role')),
                ('Year_Manumitted', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Year_Manumitted')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Image_name', models.ManyToManyField(help_text='Select Images for this Manumission', to='catalog.Image_name')),
                ('Monthly_Meeting', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Monthly_Meeting')),
                ('Page_Number', models.ManyToManyField(help_text='Page Numbers for this Manumission', to='catalog.Page_Number')),
                ('Person', models.ManyToManyField(help_text='Select Persons for this Manumission', to='catalog.Person')),
            ],
        ),
    ]
