from django.urls import path

from . import views

urlpatterns = [
    path("", views.patient_list, name="patient_list"),
    path("add/", views.patient_create, name="patient_create"),
    path("<int:pk>/edit/", views.patient_update, name="patient_update"),
    path("<int:pk>/delete/", views.patient_delete, name="patient_delete"),
]
