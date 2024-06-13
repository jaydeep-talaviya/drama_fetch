# Generated by Django 4.1.3 on 2024-06-13 02:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataclick', '0017_alter_drama_options_alter_dramaimages_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drama',
            name='casts',
            field=models.ManyToManyField(db_index=True, related_name='castsofdrama', to='dataclick.castofdrama'),
        ),
        migrations.AlterField(
            model_name='drama',
            name='directed_by',
            field=models.ManyToManyField(db_index=True, related_name='directors', to='dataclick.person'),
        ),
        migrations.AlterField(
            model_name='drama',
            name='extended_casts',
            field=models.ManyToManyField(db_index=True, related_name='extendedcasts', to='dataclick.castofdrama'),
        ),
        migrations.AlterField(
            model_name='drama',
            name='written_by',
            field=models.ManyToManyField(db_index=True, related_name='writters', to='dataclick.person'),
        ),
        migrations.AlterField(
            model_name='personimages',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='personimages', to='dataclick.person'),
        ),
    ]