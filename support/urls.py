from django.urls import path
from .views import (
    TicketListCreateView, TicketDetailView, TicketMessageListCreateView,
    TicketAttachmentDownloadView,
    NotificationListView, NotificationReadView, NotificationReadAllView,
)

app_name = 'support'

urlpatterns = [
    path('tickets/', TicketListCreateView.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<int:ticket_id>/messages/',
         TicketMessageListCreateView.as_view(), name='ticket-messages'),
    path('attachments/<int:pk>/download/',
         TicketAttachmentDownloadView.as_view(), name='attachment-download'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/read-all/', NotificationReadAllView.as_view(), name='notification-read-all'),
    path('notifications/<int:pk>/read/', NotificationReadView.as_view(), name='notification-read'),
]
