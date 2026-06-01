from django.shortcuts import redirect, render
from django.views import View


class AuthOtpView(View):
    def get(self, request):
        if request.COOKIES.get('access'):
            return redirect('/profile/')
        return render(request, 'auth/login.html')
    # def get(self, request, *args, **kwargs):
    #     if self.request.user.is_authenticated:
    #         redirect('auth:profile')
    #     return render(request, 'components/auth/login_otp.html')


class AuthOtpVerifyView(View):
    def get(self, request, *args, **kwargs):
        method = self.request.GET.get('method')
        phone = self.request.GET.get('phone')
        if self.request.user.is_authenticated:
            redirect('auth:profile')
        context = {'method': method, 'phone': phone}
        return render(request, 'auth/login.html')
        return render(request, 'components/auth/otp_verify.html', context)


class AuthPasswordView(View):
    def get(self, request):
        if request.COOKIES.get('access'):
            return redirect('/profile/')
        return render(request, 'auth/login.html')
    # def get(self, request, *args, **kwargs):
    #     if self.request.user.is_authenticated:
    #         redirect('auth:profile')
    #     return render(request, 'components/auth/login_password.html')


class LogoutView(View):
    """
    جایگزین: app/auth/logout/page.tsx
    صفحه خروج — JS توکن‌ها رو پاک و ریدایرکت می‌کنه
    """
    def get(self, request):
        return render(request, 'auth/logout.html')