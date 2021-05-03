from django.urls import reverse
from django.db import transaction
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.core.mail import mail_admins

from reversion import revisions

from core import generic_views
from . import models, forms


class BlacklistView(generic_views.LoginMixin):
    view_name = 'blacklists'
    model = models.Blacklist
    title = _('Blacklists')


class ListView(BlacklistView, TemplateView):
    template_name = 'blacklists.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_change = models.Blacklist.last_change()
        if last_change:
            context['last_change'] = (timezone.now().replace(microsecond=0) -
                                      last_change.replace(microsecond=0))
        context['blacklists'] = models.Blacklist.objects.all()
        return context


class AddView(BlacklistView, FormView):
    form_class = forms.AddForm
    template_name = 'add_form.html'

    def form_valid(self, form):
        form.save()
        mail_admins(subject="New Blacklist",
                    message="Title: {}\nType: {}".format(
                        form.cleaned_data.get('title'),
                        form.cleaned_data.get('blacklist_type'),
                    ))
        return HttpResponseRedirect(reverse('blacklists:list'))


class EditView(BlacklistView, generic_views.EditView):
    form_class = forms.EditForm
    template_name = 'edit_form.html'

    def form_valid(self, form):
        with transaction.atomic(), revisions.create_revision():
            form.save()
            revisions.set_comment(form.cleaned_data['comment'])
        mail_admins(subject="Blacklist Updated",
                    message="Title: {}\nType: {}".format(
                        form.cleaned_data.get('title'),
                        form.cleaned_data.get('blacklist_type'),
                    ))
        return HttpResponseRedirect(reverse('blacklists:list'))


class BlacklistDump(TemplateView):
    template_name = 'dump.txt'
    content_type = 'text/text'

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['urls'] = models.Blacklist.dump()
        return c


class History(BlacklistView, generic_views.HistoryView):
    """
        History log
    """
    pass
