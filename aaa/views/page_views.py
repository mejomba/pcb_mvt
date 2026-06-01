# === your_app/views/page_views.py ===
import json
from django.shortcuts import render, redirect
from django.views import View


class ProfileView(View):
    """
    جایگزین: app/profile/page.tsx
    چک کوکی server-side انجام می‌شه (مثل middleware)
    fetch داده‌های واقعی توسط JS انجام می‌شه
    """
    def get(self, request):
        if not request.COOKIES.get('access'):
            return redirect(f'/api/v1/auth/login/?next=/profile/')
        return render(request, 'profile/profile.html')