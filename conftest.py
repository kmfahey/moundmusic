#!/usr/bin/python3

import pytest
import os

from moundmusic import settings


with open(
    os.path.join(settings.BASE_DIR, "postgres_credentials.dat"), mode="r"
) as postgres_auth_file:
    username = next(postgres_auth_file).strip()
    password = next(postgres_auth_file).strip()


@pytest.fixture(scope="session")
def django_db_setup():
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "moundmusic",
        "USER": username,
        "PASSWORD": password,
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
