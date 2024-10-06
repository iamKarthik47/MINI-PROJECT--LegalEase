# Generated by Django 3.2.24 on 2024-09-01 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20240901_1226'),
    ]

    operations = [
        migrations.RenameField(
            model_name='advocates',
            old_name='pin',
            new_name='post',
        ),
        migrations.RemoveField(
            model_name='user',
            name='category',
        ),
        migrations.AddField(
            model_name='advocates',
            name='type',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
    ]