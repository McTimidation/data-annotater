from django.urls import path
from . import views 

app_name = "data_annotater"

urlpatterns = [
    path("upload/", views.upload, name="upload"),
    path("list/", views.retail_list, name="list"),
    path("edit/<int:pk>/", views.edit, name="edit"),
]
