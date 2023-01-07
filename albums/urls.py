from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # `python manage.py runserver` emits an error claiming this is unnecessary,
    # but without it then http://localhost:8000/albums/ errors out, so it stays in.
    path('/', views.index, name='index'),
]
