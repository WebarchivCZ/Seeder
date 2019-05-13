from django.urls import reverse
from django.views import View
from django.views.generic import DetailView
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.db.models import Q
from django.contrib import messages

from dal import autocomplete
from formtools.wizard.views import SessionWizardView
from datetime import datetime
from urljects import U, URLView, pk

from contracts.models import Contract
from core.generic_views import ObjectMixinFixed, MessageView
from publishers import forms as publisher_forms
from core import generic_views
from comments.views import CommentViewGeneric
from contracts import constants as contract_constants

from . import forms, models, tables, field_filters


def show_publisher_create_form(wizard):
    """
        Django form wizard condition
    """
    cleaned_data = wizard.get_cleaned_data_for_step('source') or {}
    return not cleaned_data.get('publisher', False)


def show_publisher_choose_form(wizard):
    """
        Django form wizard condition
    """
    cleaned_data = wizard.get_cleaned_data_for_step('source') or {}
    return cleaned_data.get('publisher', False)


class SourceView(generic_views.LoginMixin):
    view_name = 'sources'
    model = models.Source


class AddSource(generic_views.LoginMixin, SessionWizardView, URLView):
    template_name = 'add_source.html'
    # view_name = 'add_source'

    url = U / 'add'
    url_name = 'add'

    form_list = (
        ('source', forms.SourceForm),
        ('duplicity', forms.DuplicityForm),
        ('choose_publisher', publisher_forms.ContactChoiceForm),
        ('create_publisher', publisher_forms.PublisherForm),
    )

    template_names = {
        'duplicity': 'duplicity_check.html',
    }

    titles = {
        'source': _('Add source'),
        'create_publisher': _('Add publisher'),
        'choose_publisher': _('Choose contact person'),
        'duplicity': _('Check for duplicities'),
    }

    condition_dict = {
        'create_publisher': show_publisher_create_form,
        'choose_publisher': show_publisher_choose_form
    }

    def get_title(self):
        return self.titles[self.steps.current]

    def get_form(self, step=None, data=None, files=None):
        """
            Dynamically set source form according to user rights
        """
        step = step or self.steps.current
        is_manager = self.request.user.has_perm('core.manage_sources')
        form_class = self.form_list[step]

        if step == 'source' and is_manager:
            form_class = forms.ManagementSourceForm
            form = form_class(prefix=self.get_form_prefix(step, form_class),
                              data=data, files=files)
            owner = form.fields['owner']
            owner.initial = self.request.user
            return form

        elif step == 'choose_publisher':
            publisher = self.get_cleaned_data_for_step('source')['publisher']
            form = form_class(prefix=self.get_form_prefix(step, form_class),
                              data=data, files=files)
            contact = form.fields['contact']
            contact.queryset = publisher.contactperson_set.all()
            if contact.queryset.exists():
                contact.initial = contact.queryset.first()
            return form

        return form_class(prefix=self.get_form_prefix(step, form_class),
                          data=data, files=files)

    def get_template_names(self):
        if self.steps.current in self.template_names:
            return self.template_names[self.steps.current]
        return super().get_template_names()

    def get_duplicities(self):
        """
        Returns queryset with similar records
        """

        source_data = self.get_cleaned_data_for_step('source')
        publisher_data = self.get_cleaned_data_for_step('create_publisher')
        filters = (Q(name__icontains=source_data['name']) |
                   Q(seed__url=source_data['main_url']))
        if publisher_data:
            filters |= Q(publisher__name__icontains=publisher_data['name'])

        return models.Source.objects.filter(filters).distinct()

    def done(self, form_list, **kwargs):
        form_dict = kwargs['form_dict']
        user = self.request.user
        source_form = form_dict['source']
        publisher_new = form_dict.get('create_publisher', None)
        publisher_choice = form_dict.get('choose_publisher', None)
        is_manager = user.has_perm('core.manage_sources')

        source = source_form.save(commit=False)
        source.created_by = user

        if not is_manager or not source.created_by:
            source.owner = user

        if publisher_new:
            source.publisher, source.publisher_contact = publisher_new.save()
        if publisher_choice:
            # this forms has two modes - create new object or choose existing
            contact = publisher_choice.cleaned_data['contact']
            if not contact:
                contact = publisher_choice.save(commit=False)
                contact.publisher = source.publisher
                contact.save()
            source.publisher_contact = contact
        source.save()

        if source_form.cleaned_data['open_license']:
            contract = Contract(
                publisher=source.publisher,
                valid_from=datetime.now(),
                creative_commons=True,
                state=contract_constants.CONTRACT_STATE_VALID
            )
            contract.save()
            contract.sources.add(source)

        models.Seed(
            url=source_form.cleaned_data['main_url'],
            source=source
        ).save()

        return HttpResponseRedirect(source.get_absolute_url())


class SourceDetail(SourceView, DetailView, CommentViewGeneric, URLView):
    template_name = 'source.html'
    context_object_name = 'source'
    threaded_comments = True

    url = U / 'detail' / pk
    url_name = 'detail'


class SourceEdit(SourceView, generic_views.EditView, URLView):
    form_class = forms.SourceEditForm
    template_name = 'edit_source.html'

    url = U / 'edit' / pk
    url_name = 'edit'



class DeleteView(View, MessageView, SourceView, ObjectMixinFixed,  URLView):
    url = U / pk / 'delete'
    url_name = 'delete'

    def post(self, request, *args, **kwargs):
        s = self.get_object()

        if not request.user.is_superuser:
            self.add_message(
                _("You dont have permission for deactivating source"),
                messages.ERROR
            )
            return HttpResponseRedirect(s.get_absolute_url())

        s.active = False
        s.save()

        s.delete_blob()  # remove from search


        self.add_message(
            _('Source deactivated, it might still appear in searches.'),
            messages.SUCCESS
        )
        return HttpResponseRedirect(reverse('source:list'))


class SeedAdd(SourceView, generic_views.ObjectMixinFixed, FormView, URLView):
    form_class = forms.SeedEdit

    url = U / 'add_seed' / pk
    url_name = 'add_seed'

    title = _('Add seed')
    template_name = 'add_form.html'

    def form_valid(self, form):
        seed = form.save(commit=False)
        seed.source = self.get_object()
        seed.save()
        return HttpResponseRedirect(self.get_object().get_absolute_url())


class SeedEdit(SourceView, generic_views.EditView, URLView):
    form_class = forms.SeedEdit
    model = models.Seed

    url = U / 'seed' / pk
    url_name = 'seed_edit'


class History(SourceView, generic_views.HistoryView, URLView):
    """
        History log
    """
    url = U / 'history' / pk
    url_name = 'history'


class SourceList(SourceView, generic_views.FilteredListView, URLView):
    title = _('Sources')
    table_class = tables.SourceTable
    filter_class = field_filters.SourceFilter

    url = U / 'list'
    url_name = 'list'

    add_link = 'source:add'


class CategoryAutocomplete(autocomplete.Select2QuerySetView, URLView):
    url_name = 'category_autocomplete'
    url = U / 'category_autocomplete'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Category.objects.none()

        qs = models.Category.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.distinct()


class SubcategoryAutocomplete(autocomplete.Select2QuerySetView, URLView):
    url_name = 'subcategory_autocomplete'
    url = U / 'subcategory_autocomplete'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.SubCategory.objects.none()
        qs = models.SubCategory.objects.all()

        category = self.forwarded.get('category', None)
        if category:
            qs = qs.filter(category=category)

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.distinct()


class SourceAutocomplete(autocomplete.Select2QuerySetView, URLView):
    url_name = 'source_autocomplete'
    url = U / 'source_autocomplete'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Source.objects.none()

        qs = models.Source.objects.all()
        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(seed__url__icontains=self.q)
            )
        return qs.distinct()


class SourcePublicAutocomplete(autocomplete.Select2QuerySetView, URLView):
    url_name = 'source_public_autocomplete'
    url = U / 'source_public_autocomplete'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Source.objects.none()

        qs = models.Source.objects.archiving()
        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(seed__url__icontains=self.q)
            )
        return qs.distinct()


class KeywordAutocomplete(autocomplete.Select2QuerySetView, URLView):
    url_name = 'keyword_autocomplete'
    url = U / 'keyword_autocomplete'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.KeyWord.objects.none()

        qs = models.KeyWord.objects.all()
        if self.q:
            qs = qs.filter(word__icontains=self.q)
        return qs.distinct()


class SourceDump(URLView, TemplateView):
    url_name = 'dump'
    url = U / 'dump'
    template_name = 'dump.txt'

    content_type = 'text/text'

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['seed_urls'] = models.Seed.archiving.public_seeds().all()\
            .values_list('url', flat=True)
        return c
