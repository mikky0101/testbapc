# Generated by Django 2.2.13 on 2021-04-04 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_item_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default=' this is a decription page '),
            preserve_default=False,
        ),
    ]