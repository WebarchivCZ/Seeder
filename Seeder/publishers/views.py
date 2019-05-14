from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect

from dal import autocomplete

from core import generic_views
from comments.views import CommentViewGeneric
from . import models, forms, tables, field_filters


class PublisherView(generic_views.LoginMixin):
    view_name = 'publishers'
    model = models.Publisher


class AddPublisher(PublisherView, FormView):
    form_class = forms.PublisherForm
    template_name = 'add_form.html'
    title = _('Add publisher')

    def form_valid(self, form):
        publisher, contact = form.save()
        return HttpResponseRedirect(publisher.get_absolute_url())


class Detail(PublisherView, DetailView, CommentViewGeneric):
    template_name = 'publisher.html'


class Edit(PublisherView, generic_views.EditView):
    form_class = forms.PublisherEditForm


class History(PublisherView, generic_views.HistoryView):
    """
        History of changes to publishers
    """
    pass


class ListView(PublisherView, generic_views.FilteredListView):
    title = _('Publishers')
    table_class = tables.PublisherTable
    filter_class = field_filters.PublisherFilter

    add_link = 'publishers:add'


class EditContacts(PublisherView, FormView, generic_views.ObjectMixinFixed):  # noqa
    form_class = forms.ContactFormset
    template_name = 'formset_verbose.html'
    title = _('Edit contacts')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
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


class PublisherAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Publisher.objects.none()
        qs = models.Publisher.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class PublisherContactAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.ContactPerson.objects.none()
        qs = models.ContactPerson.objects.all()
        publisher = self.forwarded.get('publisher', None)
        if publisher:
            qs = qs.filter(publisher=publisher)

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
