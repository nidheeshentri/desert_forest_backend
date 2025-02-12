from django.urls import path
from . import views

app_name = "account"
urlpatterns = [
    path("", views.GetUserData.as_view(), name = "user_data"),
    path("forgot-password/", views.ForgorPassword.as_view(), name = "forgot_password"),
    path("register/", views.Register.as_view(), name = "register"),
    path("templates/", views.TemplateListCreateView.as_view(), name = "templates"),
    path("template/create", views.CreateTemplate.as_view(), name = "create-template"),
    path("templates/<str:pk>", views.TemplateDetailView.as_view(), name = "templates-details"),
    path("create-campaign/", views.CreateCampaign.as_view(), name = "create-campaign"),
    path("campaigns/", views.CampaignListCreateView.as_view(), name = "campaigns"),
    path("campaigns/<str:pk>", views.CampaignDetailView.as_view(), name = "campaigns-details"),
    path("messages/", views.MessageListCreateView.as_view(), name = "messages"),
    path("messages/<str:pk>", views.MessageDetailView.as_view(), name = "messages-details"),
    path("contacts/", views.ContactListCreateView.as_view(), name = "contacts"),
    path("contacts/<str:pk>", views.ContactDetailView.as_view(), name = "contacts-details"),
    path("contact-group/", views.ContactGroupListCreateView.as_view(), name = "contact-group"),
    path("contacts-group/<str:pk>", views.ContactGroupDetailView.as_view(), name = "contacts-group-details"),
    path('campaign/<int:campaign_id>/statistics/', views.CampaignStatisticsView.as_view(), name='campaign-statistics'),
    path('campaign/statistics', views.CampaignStatisticsListView.as_view(), name='campaign-statistics-list'),
]