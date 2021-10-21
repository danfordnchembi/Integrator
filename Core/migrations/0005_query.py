# Generated by Django 3.2.8 on 2021-10-20 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0004_alter_cptcode_local_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_type', models.CharField(choices=[('SVCREC', 'SVCREC'), ('DDC', 'DDC'), ('DDCOUT', 'DDCOUT'), ('REV', 'REV'), ('BEDOCC', 'BEDOCC')], max_length=100)),
                ('query', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Queries',
                'db_table': 'Queries',
            },
        ),
    ]
