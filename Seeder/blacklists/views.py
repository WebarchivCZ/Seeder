from django.core.urlresolvers import reverse
from django.db import transaction
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from reversion import revisions
from urljects import U, URLView, pk

from core import generic_views
from . import models, forms


class BlacklistView(generic_views.LoginMixin):
    view_name = 'blacklists'
    model = models.Blacklist
    title = _('Blacklists')


class ListView(BlacklistView, TemplateView, URLView):
    url_name = 'list'
    url = U
    template_name = 'blacklists.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blacklists'] = models.Blacklist.objects.all()
        return context


class AddView(BlacklistView, FormView, URLView):
    url = U / 'add'
    url_name = 'add'
    form_class = forms.AddForm
    template_name = 'add_form.html'

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('blacklists:list'))


class EditView(BlacklistView, generic_views.EditView, URLView):
    url = U / pk / 'edit'
    url_name = 'edit'
    form_class = forms.EditForm
    template_name = 'edit_form.html'

    def form_valid(self, form):
        with transaction.atomic(), revisions.create_revision():
            form.save()
            revisions.set_comment(form.cleaned_data['comment'])
        return HttpResponseRedirect(reverse('blacklists:list'))


class History(BlacklistView, generic_views.HistoryView, URLView):
    """
        History log
    """
    url = U / 'history' / pk
    url_name = 'history'
