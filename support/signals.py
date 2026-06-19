from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TicketMessage, Notification


@receiver(post_save, sender=TicketMessage)
def notify_on_new_message(sender, instance, created, **kwargs):
    if not created:
        return

    message = instance
    ticket = message.ticket
    sender_user = message.sender
    sender_id = sender_user.id if sender_user else None

    recipients = []
    if message.is_internal:
        # یادداشت داخلی: فقط به مسئول (اگر غیر از فرستنده باشد)
        if ticket.assignee_id and ticket.assignee_id != sender_id:
            recipients.append(ticket.assignee)
    elif sender_user and sender_user.is_staff:
        # پاسخ کارشناس → به مالک تیکت
        if ticket.creator_user_id and ticket.creator_user_id != sender_id:
            recipients.append(ticket.creator_user)
    else:
        # پیام مشتری → به مسئول (در صورت تخصیص)
        if ticket.assignee_id and ticket.assignee_id != sender_id:
            recipients.append(ticket.assignee)

    for r in recipients:
        Notification.objects.create(
            recipient=r, ticket=ticket, message=message,
            type=Notification.Type.NEW_MESSAGE,
            text=f"پیام جدید در تیکت {ticket.number}",
        )