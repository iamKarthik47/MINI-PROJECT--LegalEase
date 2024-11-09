# Generated by Django 5.1 on 2024-10-26 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_complaintfeedback'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvocateStatus',
            fields=[
                ('advocate', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='myapp.advocates')),
                ('status', models.CharField(default='Active', max_length=10)),
            ],
        ),
    ]
