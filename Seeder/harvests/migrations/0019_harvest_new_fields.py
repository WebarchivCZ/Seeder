# Generated by Django 2.2.20 on 2021-08-18 13:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('harvests', '0018_auto_20210809_0819'),
    ]

    operations = [
        migrations.CreateModel(
            name='HarvestConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('harvest_type', models.CharField(choices=[('serials', 'Serials'), ('topics', 'Topics'), ('tests', 'Tests'), ('totals', 'Totals')], max_length=7, unique=True, verbose_name='Harvest type')),
                ('duration', models.PositiveIntegerField(default=259200, verbose_name='duration')),
                ('budget', models.PositiveIntegerField(default=10000, verbose_name='budget')),
                ('dataLimit', models.BigIntegerField(default=10000000000, verbose_name='dataLimit')),
                ('documentLimit', models.PositiveIntegerField(default=0, verbose_name='documentLimit')),
                ('deduplication', models.CharField(default='PATH', max_length=64, verbose_name='deduplication')),
            ],
            options={
                'verbose_name': 'Harvest Configuration',
                'verbose_name_plural': 'Harvest Configurations',
                'ordering': ('harvest_type',),
            },
        ),
        migrations.AddField(
            model_name='harvest',
            name='budget',
            field=models.PositiveIntegerField(default=10000, verbose_name='budget'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='combined',
            field=models.BooleanField(default=False, verbose_name='Combined'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='dataLimit',
            field=models.BigIntegerField(default=10000000000, verbose_name='dataLimit'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='date_frozen',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date frozen'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='deduplication',
            field=models.CharField(default='PATH', max_length=64, verbose_name='deduplication'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='documentLimit',
            field=models.PositiveIntegerField(default=0, verbose_name='documentLimit'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='duration',
            field=models.PositiveIntegerField(default=259200, verbose_name='duration'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='harvest_type',
            field=models.CharField(choices=[('serials', 'Serials'), ('topics', 'Topics'), ('tests', 'Tests'), ('totals', 'Totals')], default='serials', max_length=7, verbose_name='Harvest type'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='manuals',
            field=models.BooleanField(default=False, verbose_name='Manuals'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='paraharvest',
            field=models.BooleanField(default=False, verbose_name='Paraharvest'),
        ),
    ]
