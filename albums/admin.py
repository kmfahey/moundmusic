#!/usr/bin/python3

# Because this package reuses model classes between apps, it's not possible to
# register the models with django.contrib.admin: it leads to an error of the
# form "django.contrib.admin.sites.AlreadyRegistered: The model Album is already
# registered in app 'users'."
