# Generated by Django 5.1.2 on 2024-10-27 12:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AstronomyShow",
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
                ("title", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="PlanetariumDome",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("rows", models.IntegerField()),
                ("seats_in_row", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="ShowTheme",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Reservation",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ShowSession",
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
                ("show_time", models.DateTimeField()),
                (
                    "astronomy_show",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="planetarium.astronomyshow",
                    ),
                ),
                (
                    "planetarium_dome",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="planetarium.planetariumdome",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="astronomyshow",
            name="show_theme",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="planetarium.showtheme"
            ),
        ),
        migrations.CreateModel(
            name="Ticket",
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
                ("row", models.IntegerField()),
                ("seat", models.IntegerField()),
                (
                    "reservation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to="planetarium.reservation",
                    ),
                ),
                (
                    "show_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to="planetarium.showsession",
                    ),
                ),
            ],
            options={
                "ordering": ["row", "seat"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("show_session", "row", "seat"),
                        name="unique_ticket_per_session",
                    )
                ],
            },
        ),
    ]
