# === your_app/views/help_views.py ===
from django.shortcuts import render, redirect
from django.views import View


class HelpCategoryView(View):
    """جایگزین: app/help/[slug]/page.tsx"""
    def get(self, request, slug):
        return render(request, 'help/help-category.html', {'slug': slug})


class HelpPostView(View):
    """جایگزین: app/help/post/[slug]/page.tsx"""
    def get(self, request, slug):
        return render(request, 'help/help-post.html', {'slug': slug})


class NewOrderView(View):
    """جایگزین: app/new-order/page.tsx"""
    def get(self, request):
        if not request.COOKIES.get('access'):
            return redirect('/api/v1/auth/template/otp/?next=/api/v1/pcb/template/order/')
        return render(request, 'new-order/new-order.html')


class HelpMainView(View):
    """جایگزین: app/help/page.tsx"""
    def get(self, request):
        return render(request, 'help/help-main.html')