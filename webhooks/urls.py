from . import views
from django.urls import path

app_name = "webhook"

urlpatterns = [
    path("", views.WebhooksView.as_view(), name = "webhook"),
]