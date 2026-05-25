from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from aaa.serializers.otp_send import OTPSendSerializer


class OTPSendView(APIView):
    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.save()
            return Response({"detail": "OTP sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
