from django.urls import path

from aaa.views.auth_token import CustomTokenRefreshView
from aaa.views.auth_login import LoginView
from aaa.views.auth_logout import LogoutView
from aaa.views.auth_signup import PhoneCheckAPIView, SignupView
from aaa.views.auth_views import AuthOtpView, AuthOtpVerifyView, AuthPasswordView, LogoutView
from aaa.views.otp_login import OtpLoginAPIView
from aaa.views.otp_register import OtpRegisterAPIView
from aaa.views.otp_send import OTPSendView
from aaa.views.otp_verify import OTPVerifyView
from aaa.views.page_views import ProfileView
from aaa.views.password_login_or_signup import PasswordLoginOrSignupView
from aaa.views.resend_otp import ResendOtpAPIView
from aaa.views.user_profile import UserProfileView
from aaa.views.set_password import SetPasswordView


app_name = 'auth'

# 'api/v1/auth/'
urlpatterns = [
    path('phone-check/', PhoneCheckAPIView.as_view(), name='phone_check'),  #buse
    path('otp/send/', OTPSendView.as_view(), name='auth_otp_send'),  # use
    path('resend-otp/', ResendOtpAPIView.as_view(), name='resend-otp'),  # use
    path('otp/verify/', OTPVerifyView.as_view(), name='auth_otp_verify'),  # use
    path('set-password/', SetPasswordView.as_view(), name='set-password'),  # use

    path("password-login-or-signup/", PasswordLoginOrSignupView.as_view(), name='password-login-or-signup'),  # use

    path('profile/', UserProfileView.as_view(), name='auth_profile'),  # use


    path('template/profile/', ProfileView.as_view(),  name='profile'),
    path('login/', LoginView.as_view(), name='login'),  # use
    path('loout/', LogoutView.as_view(), name='logout'),  # use
    path('template/otp/', AuthOtpView.as_view(), name='template_auth_otp'),  # use
    path('template/password/', AuthPasswordView.as_view(), name='template_auth_password'),  # use
    path('template/otp/verify/', AuthOtpVerifyView.as_view(), name='template_auth_otp_verify'),  # use

    # path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignupView.as_view(), name='auth_signup'),
    path('otp/register/', OtpRegisterAPIView.as_view(), name='otp-register'),  # use
    path('otp/login/', OtpLoginAPIView.as_view(), name='otp-login'),  # use

    # path('login/', LoginView.as_view(), name='auth_login'),
    # path('logout/', LogoutView.as_view(), name='auth_logout'),

]
