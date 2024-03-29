# Generated by Django 2.2.20 on 2022-08-26 13:06

from django.db import migrations, models


def replace_expired_with_forced(apps, schema_editor):
    Source = apps.get_model('source', 'Source')
    # State "expired" (Bez smlouvy) was removed, so instead replace it with
    # "forced" (Archivován bez smlouvy)
    Source.objects.filter(state="expired").update(state="forced")


def revert_replace_expired_with_forced(apps, schema_editor):
    """
    Since we're *losing* information with the replacement, the action cannot
    actually be reverted. However, this shouldn't be necessary since the deleted
    state is no longer useful.
    """
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('source', '0005_seed_main_seed'),
    ]

    operations = [
        migrations.RunPython(replace_expired_with_forced,
                             revert_replace_expired_with_forced),
        migrations.AlterField(
            model_name='source',
            name='state',
            field=models.CharField(choices=[('voting', 'Voting'), ('duplicity', 'Duplicated record'), ('waiting', 'Waiting for response'), ('reevaluation', 'Waiting for reevaluation'), ('technical', 'Technical review'), ('communication', 'In communication'), ('vote_accepted', 'Accepted by staff'), ('vote_declined', 'Declined by staff'), ('success', 'Archiving accepted'), ('forced', 'Archiving without publisher consent'), ('declined', 'Declined by publisher'), ('ignored', 'Publisher ignored requests'), ('terminated', 'Contract terminated')], default='voting', max_length=15, verbose_name='State'),
        ),
    ]
