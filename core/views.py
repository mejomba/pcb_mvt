from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HeaderImage
from .serializers import HeaderImageSerializer


# === your_app/views/page_views.py ===
import json
from django.shortcuts import render, redirect


class RootHomeView(View):
    """جایگزین: app/page.tsx"""
    def get(self, request):
        return render(request, 'home.html')


class HomeView(View):
    """جایگزین: app/home/page.tsx"""
    def get(self, request):
        return render(request, 'home2.html')


class HeaderImageListView(APIView):
    def get(self, request):
        items = HeaderImage.objects.all()
        serializer = HeaderImageSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)
