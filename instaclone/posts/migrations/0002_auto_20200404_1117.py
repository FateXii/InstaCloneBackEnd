# Generated by Django 3.0.5 on 2020-04-04 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='caption',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='location',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
