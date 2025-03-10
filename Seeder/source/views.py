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

from contracts.models import Contract
from core.generic_views import ObjectMixinFixed, MessageView
from publishers import forms as publisher_forms
from core import generic_views
from comments.views import CommentViewGeneric

from . import forms, models, tables, field_filters, constants


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


class SourceView(generic_views.LoginMixin, MessageView):
    view_name = 'sources'
    model = models.Source

    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, "get_object"):
            msg = (_("Zdroje se stavem 'Archivován' a 'Archivován bez smlouvy' "
                     "musí mít vybranou Frekvenci sklízení"), messages.ERROR)
            obj = self.get_object()
            if isinstance(obj, models.Source):
                # Archiving states should have Frequency set
                if (obj.state in constants.ARCHIVING_STATES and
                        obj.frequency is None):
                    self.add_message(*msg)
            elif isinstance(obj, models.Seed):
                if (obj.source.state in constants.ARCHIVING_STATES and
                        obj.source.frequency is None):
                    self.add_message(*msg)
        else:
            pass
        return super().dispatch(request, *args, **kwargs)


class AddSource(generic_views.LoginMixin, SessionWizardView):
    template_name = 'add_source.html'
    # view_name = 'add_source'

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
        # Since Keywords are Many2Many, they cannot be saved on commit=False,
        # hence save_m2m must be called on the form after committing the object
        source_form.save_m2m()

        models.Seed(
            url=source_form.cleaned_data['main_url'],
            source=source
        ).save()

        return HttpResponseRedirect(source.get_absolute_url())


class SourceDetail(SourceView, DetailView, CommentViewGeneric):
    template_name = 'source.html'
    context_object_name = 'source'
    threaded_comments = True


class SourceEdit(SourceView, generic_views.EditView):
    form_class = forms.SourceEditForm
    template_name = 'edit_source.html'


class DeleteView(View, SourceView, ObjectMixinFixed):
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


class SeedAdd(SourceView, generic_views.ObjectMixinFixed, FormView):
    form_class = forms.SeedEdit

    title = _('Add seed')
    template_name = 'add_form.html'

    def form_valid(self, form):
        seed = form.save(commit=False)
        seed.source = self.get_object()
        seed.save()
        return HttpResponseRedirect(self.get_object().get_absolute_url())


class SeedEdit(SourceView, generic_views.EditView):
    form_class = forms.SeedEdit
    model = models.Seed
    template_name = "edit_seed.html"


class SeedDelete(View, SourceView, ObjectMixinFixed):
    model = models.Seed

    def post(self, request, *args, **kwargs):
        s = self.get_object()
        redirect_url = s.get_absolute_url()
        if not request.user.is_superuser:
            self.add_message(
                _("You dont have permission for deleting seeds"),
                messages.ERROR)
            return HttpResponseRedirect(redirect_url)
        s.delete()
        self.add_message(_('Seed deleted.'), messages.SUCCESS)
        return HttpResponseRedirect(redirect_url)


class History(SourceView, generic_views.HistoryView):
    """
        History log
    """
    pass


class SourceList(SourceView, generic_views.FilteredListView):
    title = _('Sources')
    table_class = tables.SourceTable
    filterset_class = field_filters.SourceFilter

    add_link = 'source:add'

    def get_df_for_full_export(self):
        from .models import Source
        return Source.export_all_sources()


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Category.objects.none()

        qs = models.Category.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.distinct()


class SubcategoryAutocomplete(autocomplete.Select2QuerySetView):
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


class SourceAutocomplete(autocomplete.Select2QuerySetView):
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


class SourcePublicAutocomplete(autocomplete.Select2QuerySetView):
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


class KeywordAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.KeyWord.objects.none()

        qs = models.KeyWord.objects.all()
        if self.q:
            qs = qs.filter(word__icontains=self.q)
        return qs.distinct()


class SourceDump(TemplateView):
    template_name = 'dump.txt'

    content_type = 'text/text'

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['urls'] = models.Seed.objects.public_seeds(
        ).all().values_list('url', flat=True)
        return c
