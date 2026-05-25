from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from aaa.models.otp import OTP
from aaa.utils.otp import OTPAction


class ResendOtpAPIView(APIView):
    throttle_scope = 'resend_otp'

    def post(self, request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"error": "Phone number is required."}, status=400)

        recent_otp = OTP.objects.filter(phone=phone).order_by('-created_at').first()
        if recent_otp and timezone.now() - recent_otp.created_at < timedelta(seconds=6):
            return Response({"error": "You must wait before resending OTP."}, status=429)

        if recent_otp:
            recent_otp.is_used = True
            recent_otp.save()

        otp = OTPAction.perform_otp(phone, 'sms')
        OTP.objects.create(phone=phone, code=otp, expires_at=timezone.now() + timedelta(minutes=2))

        return Response({"detail": "OTP sent successfully."})