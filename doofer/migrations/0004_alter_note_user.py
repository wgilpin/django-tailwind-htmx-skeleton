# Generated by Django 5.0.4 on 2024-05-07 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doofer", "0003_note_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="user",
            field=models.IntegerField(default=0),
        ),
    ]
