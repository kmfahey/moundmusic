#!/usr/bin/python3

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:model_obj_id>', views.single_user),
    path('<int:model_obj_id>/password', views.single_user_password_set_password),
    path('<int:model_obj_id>/password/authenticate', views.single_user_password_authenticate),
    path('<int:outer_model_obj_id>/buyer_account', views.single_user_any_buyer_account),
    path('<int:outer_model_obj_id>/buyer_account/<int:inner_model_obj_id>', views.single_user_single_buyer_account),
    path('<int:outer_model_obj_id>/buyer_account/<int:inner_model_obj_id>/listings',
         views.single_user_single_buyer_account_any_listing),
    path('<int:outer_model_obj_id>/buyer_account/<int:inner_model_obj_id>/listings/<int:third_model_obj_id>',
         views.single_user_single_buyer_account_single_listing),
    path('<int:outer_model_obj_id>/seller_account', views.single_user_any_seller_account),
    path('<int:outer_model_obj_id>/seller_account/<int:inner_model_obj_id>', views.single_user_single_seller_account),
    path('<int:outer_model_obj_id>/seller_account/<int:inner_model_obj_id>/listings',
         views.single_user_single_seller_account_any_listing),
    path('<int:outer_model_obj_id>/seller_account/<int:inner_model_obj_id>/listings/<int:third_model_obj_id>',
         views.single_user_single_seller_account_single_listing),
]
