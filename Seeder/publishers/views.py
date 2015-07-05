import models
import forms
import tables
import field_filters

from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect

from core import generic_views
from comments.views import CommentViewGeneric


class PublisherView(generic_views.LoginMixin):
    view_name = 'publishers'
    model = models.Publisher


class Detail(PublisherView, DetailView, CommentViewGeneric):
    template_name = 'publisher.html'


class Edit(PublisherView, generic_views.EditView):
    form_class = forms.PublisherEditForm


class History(PublisherView, generic_views.HistoryView):
    """
        History of changes to publishers
    """


class ListView(PublisherView, generic_views.FilteredListView):
    title = _('Publishers')
    table_class = tables.PublisherTable
    filter_class = field_filters.PublisherFilter


class EditContacts(PublisherView, FormView, generic_views.ObjectMixinFixed):
    form_class = forms.ContactFormset
    template_name = 'formset_verbose.html'
    title = _('Edit contacts')

    def get_form_kwargs(self):
        kwargs = super(EditContacts, self).get_form_kwargs()
        kwargs['queryset'] = self.object.contactperson_set.all()
        return kwargs

    def form_valid(self, form):
        contacts = form.save(commit=False)
        for contact in contacts:
            contact.publisher = self.object
            contact.save()
        for obj in form.deleted_objects:
            obj.delete()

        return HttpResponseRedirect(self.object.get_absolute_url())
