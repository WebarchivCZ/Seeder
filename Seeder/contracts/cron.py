from datetime import date

from django.core.mail import send_mail
from django.utils.html import strip_tags

from . import constants
from .models import Contract, EmailNegotiation


def expire_contracts():
    today = date.today()
    expired = Contract.objects.filter(
        valid_to__lte=today,
        state=constants.CONTRACT_STATE_VALID
    )

    for contract in expired:
        print('Expiring', contract)
        contract.expire()


def send_emails():
    today = date.today()
    emails_to_send = EmailNegotiation.objects.filter(
        scheduled_date__lte=today,
        sent=False,
        contract__state=constants.CONTRACT_STATE_NEGOTIATION
    )

    for email in emails_to_send:
        send_mail(
            subject=email.title,
            message=strip_tags(email.content),
            html_message=email.content,
            from_email=email.contract.sources.first().owner.email,
            recipient_list=[email.to_email]
        )

        email.sent = True
        email.save()
