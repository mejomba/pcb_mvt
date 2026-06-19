from drf_spectacular.utils import extend_schema
from aaa.serializers.user_profile import UserProfileSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from aaa.models.profile_models import Address, LegalProfile
from aaa.serializers.user_profile import AddressSerializer, LegalProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserProfileSerializer,
        responses=UserProfileSerializer
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        request=UserProfileSerializer,
        responses=UserProfileSerializer
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnedResourceMixin:
    """
    منطق مشترک برای منابعی که به کاربر تعلق دارند و حذف نرم می‌شوند.
    کلاس فرزند باید model و serializer_class را تعریف کند.
    """
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = None

    def get_queryset(self, request):
        # فقط رکوردهای حذف‌نشده‌ی کاربر جاری
        return self.model.objects.filter(user=request.user, is_deleted=False)

    def get_object(self, request, pk):
        return get_object_or_404(self.get_queryset(request), pk=pk)


class OwnedListCreateView(OwnedResourceMixin, APIView):
    def get(self, request):
        qs = self.get_queryset(request)
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, creator_user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OwnedDetailView(OwnedResourceMixin, APIView):
    def get(self, request, pk):
        instance = self.get_object(request, pk)
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def put(self, request, pk):
        instance = self.get_object(request, pk)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(editor_user=request.user)
        return Response(serializer.data)

    def delete(self, request, pk):
        instance = self.get_object(request, pk)
        # حذف نرم
        instance.is_deleted = True
        instance.delete_date = timezone.now()
        instance.editor_user = request.user
        instance.save(update_fields=['is_deleted', 'delete_date', 'editor_user', 'update_date'])
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- آدرس ---
class AddressListCreateView(OwnedListCreateView):
    model = Address
    serializer_class = AddressSerializer


class AddressDetailView(OwnedDetailView):
    model = Address
    serializer_class = AddressSerializer


# --- پروفایل حقوقی ---
class LegalProfileListCreateView(OwnedListCreateView):
    model = LegalProfile
    serializer_class = LegalProfileSerializer


class LegalProfileDetailView(OwnedDetailView):
    model = LegalProfile
    serializer_class = LegalProfileSerializer
