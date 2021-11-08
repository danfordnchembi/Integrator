# Generated by Django 3.2.8 on 2021-11-06 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0009_payloadconfig'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payloadconfig',
            options={'verbose_name_plural': 'Payload Configs'},
        ),
        migrations.RemoveField(
            model_name='icd10codecategory',
            name='hdr_local_id',
        ),
        migrations.RemoveField(
            model_name='icd10codesubcategory',
            name='hdr_local_id',
        ),
        migrations.AddField(
            model_name='icd10codecategory',
            name='identifier',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]