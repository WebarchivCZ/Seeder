import models
import forms
import tables
import field_filters

from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect

from urljects import U, URLView, pk

from core import generic_views
from comments.views import CommentViewGeneric


class PublisherView(generic_views.LoginMixin, URLView):
    view_name = 'publishers'
    model = models.Publisher


class AddPublisher(PublisherView, FormView):
    form_class = forms.PublisherForm
    view_name = 'publisher_add'
    template_name = 'add_form.html'
    title = _('Add publisher')

    url = U / 'add'
    url_name = 'add'

    def form_valid(self, form):
        publisher, contact = form.save()
        return HttpResponseRedirect(publisher.get_absolute_url())


class Detail(PublisherView, DetailView, CommentViewGeneric):
    template_name = 'publisher.html'

    url = U / pk / 'detail'
    url_name = 'detail'


class Edit(PublisherView, generic_views.EditView):
    form_class = forms.PublisherEditForm

    url = U / pk / 'edit'
    url_name = 'edit'


class History(PublisherView, generic_views.HistoryView):
    """
        History of changes to publishers
    """

    url = U / pk / 'history'
    url_name = 'history'


class ListView(PublisherView, generic_views.FilteredListView):
    title = _('Publishers')
    table_class = tables.PublisherTable
    filter_class = field_filters.PublisherFilter

    url = U
    url_name = 'list'


class EditContacts(PublisherView, FormView, generic_views.ObjectMixinFixed):
    form_class = forms.ContactFormset
    template_name = 'formset_verbose.html'
    title = _('Edit contacts')

    url = U / pk / 'contacts'
    url_name = 'edit_contacts'

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
