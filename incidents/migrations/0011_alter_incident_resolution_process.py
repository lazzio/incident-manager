# Generated by Django 5.1.6 on 2025-03-22 21:19

import django_quill.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("incidents", "0010_alter_incident_impact"),
    ]

    operations = [
        migrations.AlterField(
            model_name="incident",
            name="resolution_process",
            field=django_quill.fields.QuillField(),
        ),
    ]
