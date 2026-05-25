from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class LogoutView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            xponse = Response({'detail': 'Logout successful'}, status=200)
            xponse.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
            return xponse
        except TokenError:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
