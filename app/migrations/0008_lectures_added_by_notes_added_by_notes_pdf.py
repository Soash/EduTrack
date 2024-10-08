# Generated by Django 5.1.1 on 2024-09-13 09:46

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_student_added_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='lectures',
            name='added_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lectures_added', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notes',
            name='added_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notes_added', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notes',
            name='pdf',
            field=models.FileField(blank=True, null=True, upload_to='notes_pdfs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
    ]
