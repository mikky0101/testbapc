# Generated by Django 2.2.13 on 2021-06-30 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20210628_0906'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='overview',
            field=models.CharField(default='mike', max_length=20),
            preserve_default=False,
        ),
    ]
