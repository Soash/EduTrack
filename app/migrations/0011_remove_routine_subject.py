# Generated by Django 5.1.1 on 2024-09-13 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_routine_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='routine',
            name='subject',
        ),
    ]
