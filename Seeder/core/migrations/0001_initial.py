# Generated by Django 2.2.28 on 2024-08-29 14:18

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('webarchive_size', models.CharField(default='595 TB', max_length=128)),
                ('wayback_maintenance', models.BooleanField(default=False)),
                ('wayback_maintenance_text_cs', ckeditor.fields.RichTextField(default='\n<p><span style="font-size:24px">Pokud vidíte tuto stránku, <strong>probíhá údržba dat</strong> a v archivu nelze nyní vyhledávat. Některé linky vrátí chybu.</span></p>\n<p><span style="font-size:24px">Prosím zkuste načíst Webarchiv později.</span></p>\n')),
                ('wayback_maintenance_text_en', ckeditor.fields.RichTextField(default='\n<p><span style="font-size:24px">If you see this page, <strong>we are currently doing maintenance</strong> and it is not possible to search the archive. Some links may return an error.</span></p>\n<p><span style="font-size:24px">Please, try to load Webarchiv again later.</span></p>\n')),
            ],
            options={
                'verbose_name': 'Site Configuration',
            },
        ),
    ]
