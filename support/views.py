from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

from .models import Ticket, TicketMessage, TicketAttachment
from .serializers import (
    TicketListSerializer, TicketDetailSerializer, TicketCreateSerializer,
    TicketUpdateSerializer, TicketMessageSerializer, TicketMessageCreateSerializer,
    NotificationSerializer, create_attachments,
)
from .models import Ticket, TicketMessage, TicketAttachment, Notification



def tickets_for(user):
    qs = Ticket.objects.filter(is_deleted=False)
    if user.is_staff:
        return qs
    return qs.filter(creator_user=user)


def apply_filters(qs, params, user):
    """فیلترهای لیست تیکت (مخصوصاً برای کارشناس)."""
    if params.get('status'):
        qs = qs.filter(status=params['status'])
    if params.get('priority'):
        qs = qs.filter(priority=params['priority'])
    if params.get('category'):
        qs = qs.filter(category=params['category'])
    if params.get('overdue') in ('1', 'true', 'True'):
        qs = qs.filter(first_response_at__isnull=True,
                       first_response_due__lt=timezone.now())

    assignee = params.get('assignee')
    if assignee == 'me':
        qs = qs.filter(assignee=user)
    elif assignee:
        qs = qs.filter(assignee_id=assignee)

    if params.get('unassigned') in ('1', 'true', 'True'):
        qs = qs.filter(assignee__isnull=True)

    q = params.get('q')
    if q:
        qs = qs.filter(subject__icontains=q)
    return qs


def apply_status_workflow(ticket, sender, is_internal):
    if is_internal:
        return
    update_fields = ['status', 'editor_user', 'update_date']
    if sender.is_staff:
        ticket.status = Ticket.Status.AWAITING_CUSTOMER
        if ticket.first_response_at is None:
            ticket.first_response_at = timezone.now()
            update_fields.append('first_response_at')
    else:
        ticket.status = Ticket.Status.AWAITING_SUPPORT
    ticket.editor_user = sender
    ticket.save(update_fields=update_fields)


class TicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        summary="لیست تیکت‌ها",
        description="کارشناس همه را می‌بیند؛ مشتری فقط تیکت‌های خودش را. "
                    "فیلترها برای پنل کارشناسی کاربردی‌اند.",
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             enum=[c[0] for c in Ticket.Status.choices],
                             description="فیلتر وضعیت"),
            OpenApiParameter('priority', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             enum=[c[0] for c in Ticket.Priority.choices],
                             description="فیلتر اولویت"),
            OpenApiParameter('category', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             enum=[c[0] for c in Ticket.Category.choices],
                             description="فیلتر دسته"),
            OpenApiParameter('assignee', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="شناسه‌ی کارشناس، یا `me` برای تیکت‌های محول‌شده به خودم"),
            OpenApiParameter('unassigned', OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                             description="فقط تیکت‌های بدون مسئول"),
            OpenApiParameter('q', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description="جستجو در موضوع"),
        ],
        responses={200: TicketListSerializer(many=True)},
    )
    def get(self, request):
        qs = apply_filters(tickets_for(request.user), request.query_params, request.user)
        serializer = TicketListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary="ایجاد تیکت جدید",
        description="تیکت + اولین پیام را می‌سازد. برای پیوست فایل، درخواست را "
                    "`multipart/form-data` بفرستید و فایل‌ها را در فیلد `files` بگذارید. "
                    "بدون فایل می‌توانید JSON هم بفرستید.",
        request=TicketCreateSerializer,
        responses={201: TicketDetailSerializer},
        parameters=[OpenApiParameter('overdue', OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                    description="تیکت‌های بدون پاسخ که از مهلت SLA گذشته‌اند")],
        examples=[
            OpenApiExample(
                "تیکت عمومی",
                value={"subject": "مشکل ورود", "priority": "normal",
                       "category": "technical", "message": "نمی‌توانم وارد شوم."},
                request_only=True,
            ),
            OpenApiExample(
                "تیکت متصل به سفارش",
                value={"subject": "تاخیر سفارش", "priority": "high",
                       "category": "billing", "message": "سفارشم نرسیده.",
                       "related_type": "pcb.order", "related_id": 42},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = TicketCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        out = TicketDetailSerializer(ticket, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(tickets_for(request.user), pk=pk)

    @extend_schema(summary="جزئیات تیکت", responses={200: TicketDetailSerializer})
    def get(self, request, pk):
        ticket = self.get_object(request, pk)
        return Response(TicketDetailSerializer(ticket, context={'request': request}).data)

    @extend_schema(
        summary="ویرایش تیکت (فقط کارشناس)",
        request=TicketUpdateSerializer,
        responses={200: TicketDetailSerializer},
    )
    def patch(self, request, pk):
        if not request.user.is_staff:
            raise PermissionDenied("فقط کارشناس پشتیبانی می‌تواند تیکت را ویرایش کند.")
        ticket = self.get_object(request, pk)
        serializer = TicketUpdateSerializer(ticket, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(editor_user=request.user)
        return Response(TicketDetailSerializer(ticket, context={'request': request}).data)

    @extend_schema(
        summary="حذف نرم تیکت (فقط کارشناس)",
        responses={204: OpenApiResponse(description="تیکت حذف شد.")},
    )
    def delete(self, request, pk):
        if not request.user.is_staff:
            raise PermissionDenied("فقط کارشناس پشتیبانی می‌تواند تیکت را حذف کند.")
        ticket = self.get_object(request, pk)
        ticket.is_deleted = True
        ticket.delete_date = timezone.now()
        ticket.editor_user = request.user
        ticket.save(update_fields=['is_deleted', 'delete_date', 'editor_user', 'update_date'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class TicketMessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_ticket(self, request, ticket_id):
        return get_object_or_404(tickets_for(request.user), pk=ticket_id)

    @extend_schema(
        summary="تاریخچه‌ی گفتگوی تیکت",
        responses={200: TicketMessageSerializer(many=True)},
    )
    def get(self, request, ticket_id):
        ticket = self.get_ticket(request, ticket_id)
        qs = ticket.messages.filter(is_deleted=False)
        if not request.user.is_staff:
            qs = qs.filter(is_internal=False)
        return Response(
            TicketMessageSerializer(qs, many=True, context={'request': request}).data
        )

    @extend_schema(
        summary="افزودن پیام (با امکان پیوست فایل)",
        description="برای پیوست، `multipart/form-data` با فیلد `files` بفرستید. "
                    "`is_internal=true` فقط برای کارشناس اعمال می‌شود.",
        request=TicketMessageCreateSerializer,
        responses={201: TicketMessageSerializer},
    )
    def post(self, request, ticket_id):
        ticket = self.get_ticket(request, ticket_id)
        serializer = TicketMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_internal = serializer.validated_data.get('is_internal', False)
        if is_internal and not request.user.is_staff:
            is_internal = False

        message = TicketMessage.objects.create(
            ticket=ticket, sender=request.user,
            body=serializer.validated_data['body'],
            is_internal=is_internal, creator_user=request.user,
        )
        create_attachments(message, serializer.validated_data.get('files', []), request.user)
        apply_status_workflow(ticket, request.user, is_internal)

        return Response(
            TicketMessageSerializer(message, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class TicketAttachmentDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="دانلود محافظت‌شده‌ی پیوست",
        description="فقط مالک تیکت یا کارشناس می‌تواند فایل را دانلود کند. "
                    "پیوست‌های یادداشت داخلی برای مشتری در دسترس نیست.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, pk):
        user = request.user
        # دامنه‌ی دسترسی با همان tickets_for کنترل می‌شود (مالک یا کارشناس، تیکت حذف‌نشده)
        attachment = get_object_or_404(
            TicketAttachment.objects.filter(
                is_deleted=False,
                message__is_deleted=False,
                message__ticket__in=tickets_for(user),
            ),
            pk=pk,
        )
        # پیوستِ یادداشت داخلی برای غیرکارشناس → ۴۰۴ (تا حتی وجودش لو نرود)
        if not user.is_staff and attachment.message.is_internal:
            raise Http404

        response = FileResponse(
            attachment.file.open('rb'),
            as_attachment=True,
            filename=attachment.original_name or attachment.file.name.rsplit('/', 1)[-1],
        )
        if attachment.mime_type:
            response['Content-Type'] = attachment.mime_type
        return response


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="لیست اعلان‌های من",
        parameters=[
            OpenApiParameter('unread', OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                             description="فقط اعلان‌های خوانده‌نشده"),
        ],
        responses={200: NotificationSerializer(many=True)},
    )
    def get(self, request):
        qs = Notification.objects.filter(recipient=request.user)
        if request.query_params.get('unread') in ('1', 'true', 'True'):
            qs = qs.filter(is_read=False)
        return Response(NotificationSerializer(qs, many=True).data)


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="علامت‌گذاری یک اعلان به‌عنوان خوانده‌شده",
        request=None,
        responses={204: OpenApiResponse(description="انجام شد")},
    )
    def post(self, request, pk):
        n = get_object_or_404(Notification.objects.filter(recipient=request.user), pk=pk)
        if not n.is_read:
            n.is_read = True
            n.read_date = timezone.now()
            n.save(update_fields=['is_read', 'read_date'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="خواندن همه‌ی اعلان‌ها",
        request=None,
        responses={204: OpenApiResponse(description="انجام شد")},
    )
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True, read_date=timezone.now()
        )
        return Response(status=status.HTTP_204_NO_CONTENT)