# Generated by Django 5.1.6 on 2025-02-23 20:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("incidents", "0003_alter_incident_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="incident",
            name="category",
            field=models.CharField(
                choices=[("categorie", "Catégorie"), ("autre", "Autre")],
                default="categorie",
                max_length=20,
            ),
        ),
    ]
