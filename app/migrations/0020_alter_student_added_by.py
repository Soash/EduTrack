# Generated by Django 5.1.1 on 2024-09-22 08:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_alter_result_symbol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='added_by',
            field=models.ForeignKey(blank=True, default='Self Registered', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_added', to=settings.AUTH_USER_MODEL),
        ),
    ]
