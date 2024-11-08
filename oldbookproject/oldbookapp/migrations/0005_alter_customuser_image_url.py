# Generated by Django 5.1.1 on 2024-10-11 16:50

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("oldbookapp", "0004_cartitem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="image_url",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=django.core.files.storage.FileSystemStorage(location=""),
                upload_to="profile_images/",
            ),
        ),
    ]
