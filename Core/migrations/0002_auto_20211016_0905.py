# Generated by Django 3.2.8 on 2021-10-16 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cptcode',
            old_name='local_id',
            new_name='hdr_local_id',
        ),
        migrations.RenameField(
            model_name='cptcodecategory',
            old_name='local_id',
            new_name='hdr_local_id',
        ),
        migrations.RenameField(
            model_name='cptcodesubcategory',
            old_name='local_id',
            new_name='hdr_local_id',
        ),
        migrations.RenameField(
            model_name='icd10code',
            old_name='local_id',
            new_name='hdr_local_id',
        ),
        migrations.RenameField(
            model_name='icd10codecategory',
            old_name='local_id',
            new_name='hdr_local_id',
        ),
        migrations.RenameField(
            model_name='icd10codesubcategory',
            old_name='local_id',
            new_name='hdr_local_id',
        ),
        migrations.RenameField(
            model_name='icd10subcode',
            old_name='local_id',
            new_name='hdr_local_id',
        ),
    ]