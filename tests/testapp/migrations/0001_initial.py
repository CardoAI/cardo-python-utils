# Generated by Django 4.0.1 on 2022-02-04 14:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'test_company',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=20, max_digits=40, null=True)),
                ('f_amount', models.FloatField(null=True)),
                ('tax', models.DecimalField(decimal_places=20, default=5, max_digits=40)),
                ('issue_date', models.DateField()),
                ('sector_label', models.PositiveSmallIntegerField(
                    choices=[(0, 'Unknown'), (1, 'Sector A'), (2, 'Sector B'), (3, 'Sector C')], default=0)),
                ('updated_at', models.DateField(null=True)),
                ('active', models.BooleanField(default=True)),
                ('history_info', models.JSONField(default={})),
                ('created_at', models.DateTimeField(null=True)),
                ('company', models.ForeignKey(help_text='company this invoice belongs to', null=True,
                                              on_delete=django.db.models.deletion.CASCADE,
                                              to='helper_functions_module.company')),
            ],
            options={
                'db_table': 'test_invoice',
            },
        ),
    ]
