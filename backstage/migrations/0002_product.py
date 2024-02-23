# Generated by Django 4.2.10 on 2024-02-23 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("backstage", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("price", models.FloatField(verbose_name=10)),
                ("stock", models.IntegerField(verbose_name=10)),
                ("description", models.TextField(null=True)),
                ("url", models.TextField(null=True)),
                (
                    "categoryID",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="backstage.productcategory",
                    ),
                ),
            ],
        ),
    ]
