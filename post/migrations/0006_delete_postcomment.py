# Generated by Django 5.1.3 on 2024-12-10 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0005_delete_reply'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PostComment',
        ),
    ]
