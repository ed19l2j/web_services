# Generated by Django 4.1.6 on 2023-05-09 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airline", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="bookinginstance",
            name="pending",
            field=models.BooleanField(default=True),
        ),
    ]