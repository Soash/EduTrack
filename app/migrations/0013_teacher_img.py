# Generated by Django 5.1.1 on 2024-09-14 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_exam_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='teacher_images/'),
        ),
    ]
