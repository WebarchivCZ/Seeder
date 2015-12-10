import constants

from datetime import date
from django_cron import CronJobBase, Schedule

from django.core.mail import send_mail
from django.utils.html import strip_tags

from models import Contract, EmailNegotiation
from source import constants as source_constants


class ExpireContracts(CronJobBase):
    schedule = Schedule(run_every_mins=60)

    code = 'contracts.ExpireContracts'

    def do(self):
        today = date.today()
        expired = Contract.objects.filter(
            valid_to=today,
            state=constants.CONTRACT_STATE_VALID)

        for contract in expired:
            print 'Expiring', contract
            contract.state = constants.CONTRACT_STATE_EXPIRED
            contract.source.state = source_constants.STATE_CONTRACT_EXPIRED
            contract.save()
            contract.source.save()


class SendEmails(CronJobBase):
    schedule = Schedule(run_every_mins=60)

    code = 'contracts.SendEmails'

    def do(self):
        today = date.today()
        emails_to_send = EmailNegotiation.objects.filter(
            scheduled_date__lte=today,
            sent=False,
            contract__state=constants.CONTRACT_STATE_NEGOTIATION,
            contract__in_communication=False,
            contract__source__publisher_contact__isnull=False)

        for email in emails_to_send:
            send_mail(
                subject=email.title,
                message=strip_tags(email.content),
                html_message=email.content,
                from_email=email.contract.source.owner.email,
                recipient_list=[email.contract.source.publisher_contact.email])
            email.sent = True
            email.save()
