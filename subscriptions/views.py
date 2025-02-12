from django.shortcuts import render
from .models import Subscription
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    permission_classes = [permissions.IsAdmin]
    serializer_class = SubscriptionSerializer

class SubscriptionListCreateView(generics.ListCreateAPIView):
    pass