# Generated by Django 3.0.3 on 2020-02-22 22:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_post_content'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='content',
            new_name='my_field',
        ),
    ]
