from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated

from aaa.serializers.user_serializer import SetPasswordSerializer


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SetPasswordSerializer,
        responses={
            200: inline_serializer(
                name='SetPasswordResponse',
                fields={
                    "message": serializers.CharField(),
                }
            ),
            400: inline_serializer(
                name='SetPasswordResponse',
                fields={
                    "message": serializers.CharField(),
                }
            ),
        }
    )
    def post(self, request):
        user = request.user

        # اگر یوزر قبلاً رمز معتبر داشته باشد، این اندپوینت اجازه‌ی تغییر نمی‌دهد
        # if user.has_usable_password():
        #     return Response(
        #         {"detail": "شما قبلاً رمز عبور تنظیم کرده‌اید."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['password'])
        user.save(update_fields=['password', 'update_date'])

        return Response(
            {"detail": "رمز عبور با موفقیت تنظیم شد."},
            status=status.HTTP_200_OK
        )
