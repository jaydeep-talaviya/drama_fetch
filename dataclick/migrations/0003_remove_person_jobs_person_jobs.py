# Generated by Django 4.1.3 on 2022-11-26 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataclick', '0002_person_personimages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='jobs',
        ),
        migrations.AddField(
            model_name='person',
            name='jobs',
            field=models.ManyToManyField(related_name='jobs', to='dataclick.jobs'),
        ),
    ]
