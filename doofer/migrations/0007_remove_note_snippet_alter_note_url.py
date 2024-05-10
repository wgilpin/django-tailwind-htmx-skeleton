# Generated by Django 5.0.4 on 2024-05-10 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doofer", "0006_remove_note_content_alter_note_comment_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="note",
            name="snippet",
        ),
        migrations.AlterField(
            model_name="note",
            name="url",
            field=models.URLField(blank=True, max_length=2000),
        ),
    ]
