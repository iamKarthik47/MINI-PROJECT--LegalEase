# Generated by Django 5.1 on 2024-09-22 03:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_auto_20240901_1313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='SCHEDULE',
        ),
        migrations.AddField(
            model_name='booking',
            name='ADVOCATE',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.advocates'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
