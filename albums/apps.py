#!/usr/bin/python3

from django.apps import AppConfig


class AlbumsConfig(AppConfig):
    name = "albums"
    verbose_name = "Albums"
    default_auto_field = "django.db.models.BigAutoField"
