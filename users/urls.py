#!/usr/bin/python3

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:model_obj_id>', views.single_user),
    path('<int:model_obj_id>/password', views.single_user_password_set_password),
    path('<int:model_obj_id>/password/authenticate', views.single_user_password_authenticate),
]
