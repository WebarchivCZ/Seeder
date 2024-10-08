import re
import pandas as pd
from typing import Any
from urllib.parse import urlparse
from datetime import date

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.http.response import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.db.models import Sum, When, Case, IntegerField, Q, Min, Max, Count
from django.db.models.functions import TruncDay
from django.core.paginator import EmptyPage
from django.urls import reverse
from django.conf import settings

from core.utils import get_wayback_url
from contracts.models import Contract
from search_blob.models import Blob
from settings.base import WAYBACK_URL
from source.models import Source, Category, SubCategory, KeyWord
from source.constants import PUBLIC_STATES
from harvests.models import ExternalTopicCollection
from paginator.paginator import CustomPaginator
from www.forms import NominationForm
from www.models import Nomination, SearchLog
from django_tables2.views import MultiTableMixin

from . import models
from .models import ExtinctWebsite as EW
from . import forms
from . import constants
from .tables import ExtinctWebsitesTable

ITEMS_PER_PAGE = 12


class PaginatedView:
    per_page = ITEMS_PER_PAGE

    def get_page_num(self):
        try:
            return int(self.request.GET.get('page', 1))
        except ValueError:
            return 1

    def get_paginator(self):
        paginator = CustomPaginator(
            self.get_paginator_queryset(),
            self.per_page)
        page = self.get_page_num()
        try:
            sources = paginator.page(page)
        except EmptyPage:
            sources = paginator.page(1)
        return sources

    def get_paginator_queryset(self):
        raise NotImplementedError


class Index(TemplateView):
    template_name = 'index.html'
    view_name = 'index'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'contract_count': Contract.objects.valid().count(),
            'last_sources': Source.objects.public().order_by('-created')[:5],
            'news_article': models.NewsObject.objects.filter(active=True).first(),
            'big_search_form': forms.BigSearchForm(data=self.request.GET),
            'hide_search_box': True,
        })
        return context


class TopicCollections(PaginatedView, TemplateView):
    template_name = 'topic_collections/list.html'
    view_name = 'topic_collections'
    sub_view_name = 'topic_collections'

    def get_queryset(self):
        qs = super(TopicCollections, self).get_queryset()
        return qs.filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections'] = self.get_paginator()
        return context

    def get_paginator_queryset(self):
        return ExternalTopicCollection.objects.filter(active=True)


class TopicCollectionDetail(PaginatedView, DetailView):
    template_name = 'topic_collections/detail.html'
    view_name = 'topic_collections'

    model = ExternalTopicCollection
    context_object_name = 'collection'
    per_page = 6

    def get_queryset(self):
        qs = super(TopicCollectionDetail, self).get_queryset()
        return qs.filter(active=True)

    def get_paginator_queryset(self):
        qs = self.get_object().custom_sources
        # Manually first select the PUBLIC sources and then everything else
        pks = list(
            qs.filter(state__in=PUBLIC_STATES).values_list("pk", flat=True))
        pks += list(
            qs.exclude(state__in=PUBLIC_STATES).values_list("pk", flat=True))
        # In order to return a real QS, must do some Case-When magic
        preserved = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(pks)])
        return qs.filter(pk__in=pks).order_by(preserved)

    def get_context_data(self, **kwargs):
        """
        We need to display two kind of objects on each page:
        - custom sources
        - custom seeds
        so we need to decide which paginator is longer and use that for range
        """
        context = super().get_context_data(**kwargs)
        custom_seeds = [
            {
                'name': urlparse(url).netloc,
                'url': url,
                'wayback_url': get_wayback_url(url)
            }
            for url in set(self.get_object().custom_seeds.split())
        ]

        page = self.get_page_num()
        source_paginator = CustomPaginator(
            self.get_paginator_queryset(),
            self.per_page
        )
        seed_paginator = CustomPaginator(
            custom_seeds,
            self.per_page
        )

        try:
            sources = source_paginator.page(page)
        except EmptyPage:
            sources = []

        try:
            seed_page = seed_paginator.page(page)
        except EmptyPage:
            seed_page = []

        bigger_paginator = (
            sources if source_paginator.num_pages > seed_paginator.num_pages
            else seed_page
        )

        context['source_paginator'] = sources
        context['custom_seeds'] = seed_page
        context['bigger_paginator'] = bigger_paginator
        return context


class TopicCollectionUrlsCsv(DetailView):
    model = ExternalTopicCollection

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(active=True)

    def get(self, request, *args, **kwargs):
        import csv
        self.object = self.get_object()
        # Create a CSV response and write each seed on a new row
        res = HttpResponse(content_type="text/csv")
        res["Content-Disposition"] = 'attachment; filename="urls.csv"'
        writer = csv.writer(res)
        for seed in self.object.get_seeds():
            writer.writerow([seed])
        return res


class About(TemplateView):
    template_name = 'about/about.html'
    view_name = 'about'
    sub_view_name = 'about'


class MoreAbout(TemplateView):
    template_name = 'about/more_about.html'
    view_name = 'about'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['footerFullBorder'] = True
        return context


class AboutHarvest(TemplateView):
    template_name = 'about/harvests.html'
    view_name = 'about'
    sub_view_name = 'harvests'


class AboutTerminology(TemplateView):
    template_name = 'about/terminology.html'
    view_name = 'about'
    sub_view_name = 'terminology'


class AboutDocuments(TemplateView):
    template_name = 'about/documents.html'
    view_name = 'about'
    sub_view_name = 'documents'


class AboutGraphics(TemplateView):
    template_name = 'about/graphics.html'
    view_name = 'about'
    sub_view_name = 'graphics'


class AboutContact(TemplateView):
    template_name = 'about/contact.html'
    view_name = 'about'
    sub_view_name = 'contact'


class AboutFAQ(TemplateView):
    template_name = 'about/faq.html'
    view_name = 'about'
    sub_view_name = 'faq'


class CategoryBaseView(PaginatedView):
    template_name = 'categories/categories.html'
    view_name = 'categories'

    def get_categories_context(self):
        return {
            'sources_total': Source.objects.public().count(),
            'categories': Category.objects.all().annotate(
                num_sources=Sum(
                    Case(
                        When(source__state__in=PUBLIC_STATES, then=1),
                        default=0, output_field=IntegerField()
                    )
                )
            ).filter(num_sources__gt=0)
        }

    def get_categories_detail_context(self, category):
        sub_categories = SubCategory.objects.filter(category=category)\
            .annotate(
                num_sources=Sum(
                    Case(
                        When(source__state__in=PUBLIC_STATES, then=1),
                        default=0, output_field=IntegerField()
                    )
                ))\
            .filter(num_sources__gt=0)

        return {
            'sub_categories': sub_categories,
            'cat_sources_total': category.source_set.filter(
                state__in=PUBLIC_STATES
            ).count(),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_categories_context())
        context['sources'] = self.get_paginator()
        context['startswith_options'] = \
            constants.ALPHABET_SEARCH_CONVERSION.keys()
        return context


class Categories(CategoryBaseView, TemplateView):
    def get_current_startswith(self):
        # Get the "startswith" URL parameter if present
        try:
            return str(self.request.GET.get('startswith')).strip()
        except ValueError:
            return None

    def get_paginator_queryset(self):
        startswith = self.get_current_startswith()
        # Filter by "startswith" if exists using a regex conversion chart
        if startswith is not None:
            startre = constants.ALPHABET_SEARCH_CONVERSION.get(startswith, '.')
            return Source.objects.public().filter(
                name__iregex=rf'^{startre}.*$')
        return Source.objects.public()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CategoryDetail(CategoryBaseView, DetailView):
    model = Category
    context_object_name = 'current_category'

    def get_paginator_queryset(self):
        return Source.objects.public().filter(
            Q(category=self.get_object()) |
            Q(sub_category__category=self.get_object())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = self.get_object()
        context.update(self.get_categories_detail_context(self.get_object()))
        return context


class SubCategoryDetail(CategoryBaseView, DetailView):
    model = SubCategory
    context_object_name = 'current_sub_category'

    def get_paginator_queryset(self):
        return Source.objects.public().filter(
            sub_category=self.get_object()
        )

    def get_context_data(self, **kwargs):
        category = self.get_object().category

        context = super().get_context_data(**kwargs)
        context['current_category'] = category
        context.update(self.get_categories_detail_context(category))
        return context


class ChangeListView(View):
    def get(self, request, list_type):
        self.request.session['list_type'] = list_type
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class KeywordViews(PaginatedView, DetailView):
    model = KeyWord
    context_object_name = 'keyword'
    view_name = 'index'

    template_name = 'keyword.html'

    def get_paginator_queryset(self):
        return Source.objects.public().filter(
            keywords=self.get_object()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = self.get_paginator()
        return context


class SearchRedirectView(View):
    def get(self, request):
        query = self.request.GET.get('query', '')

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        SearchLog(
            search_term=query,
            ip_address=ip,
        ).save()

        regex_is_url = (
            # SCHEME:
            r"((https?|ftp)\:\/\/)?"
            # User and Pass:
            "([a-z0-9+!*(),;?&=\$_.-]+(\:[a-z0-9+!*(),;?&=\$_.-]+)?@)?"
            # Host or IP:
            "([a-z0-9-.]*)\.([a-z]{2,4})"
            # Port:
            "(\:[0-9]{2,5})?"
            # Path:
            "(\/([a-z0-9+\$_-]\.?)+)*\/?"
            # GET Query:
            "(\?[a-z+&\$_.-][a-z0-9;:@&%=+\/\$_.-]*)?"
            # Anchor:
            "(#[a-z_.-][a-z0-9+\$_.-]*)?"
        )

        if re.match(regex_is_url, query.lower()):
            redirect_url = get_wayback_url(query)
        else:
            redirect_url = reverse('www:search', kwargs={'query': query})
        return HttpResponseRedirect(redirect_url)


class SearchView(PaginatedView, TemplateView):
    template_name = 'search.html'
    view_name = 'index'

    def get_query(self):
        return self.kwargs['query']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = self.get_query()
        if not query:
            return Source.objects.none()

        results = Blob.search_paginator(
            query,
            self.request.GET.get('page', 1),
            is_public=True
        )

        sources = [
            s.record_object for s in results.object_list
            if isinstance(s.record_object, Source)
        ]

        if len(sources) == 1:
            single_source = sources[0]
        else:
            single_source = None

        context.update({
            "results": results,
            "sources": sources,
            "single_source": single_source,
            "query": self.get_query(),
        })
        return context


class SourceDetail(DetailView):
    model = Source
    context_object_name = 'source'
    template_name = 'source_public.html'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            return super(SourceDetail, self).get(request, *args, **kwargs)
        except Http404:
            redirect_url = reverse(
                'www:search',
                kwargs={'query': self.kwargs['slug']}
            )
            return HttpResponseRedirect(redirect_url)

    def get_queryset(self):
        return Source.objects.public()


class Nominate(FormView):
    model = Nomination
    form_class = NominationForm
    view_name = 'nominate'
    sub_view_name = 'nominate'

    template_name = 'nominate/nominate.html'

    def form_valid(self, form):
        nomination = form.save()
        if nomination.submitted_by_author:
            title = _(
                'Webarchiv.cz - archivace vasich webovych stranek %(url)s') % {"url": nomination.url}
            email_template = 'nominate/emails/nomination_confirmation_owner.html'
        else:
            title = _(
                'Webarchiv.cz - archivace webovych stranek %(url)s') % {"url": nomination.url}
            email_template = 'nominate/emails/nomination_confirmation.html'

        content = render_to_string(email_template)
        notification_content = render_to_string(
            'nominate/emails/nomination_notification.html',
            {'nomination': nomination}
        )

        # Send email to user who nominated the site
        send_mail(
            subject=title,
            message=strip_tags(content),
            html_message=content,
            from_email=settings.WEBARCHIV_EMAIL,
            recipient_list=[
                nomination.contact_email,
            ]
        )

        # send notification to curators
        send_mail(
            subject=_('New nomination %(url)s') % {"url": nomination.url},
            message=strip_tags(notification_content),
            html_message=notification_content,
            from_email=settings.WEBARCHIV_EMAIL,
            recipient_list=[
                settings.WEBARCHIV_EMAIL
            ]
        )
        return super(Nominate, self).form_valid(form)

    def get_success_url(self):
        return reverse('www:nominate_success')


class NominateSuccess(TemplateView):
    template_name = 'nominate/nominate_success.html'
    view_name = 'nominate'
    sub_view_name = 'nominate_success'


class NominateContractView(TemplateView):
    template_name = 'nominate/contract.html'
    view_name = 'nominate'

    def get_context_data(self, **kwargs):
        c = super(NominateContractView, self).get_context_data(**kwargs)
        c['show_contract_link'] = True
        return c


class NominateCooperationView(TemplateView):
    template_name = 'nominate/cooperation.html'
    view_name = 'nominate'
    sub_view_name = 'nominate_cooperation'


class NominateCreativeCommonsView(TemplateView):
    template_name = 'nominate/creative_commons.html'
    view_name = 'nominate'
    sub_view_name = 'nominate_creative_commons'


class NominateSourceSelectionView(TemplateView):
    template_name = 'nominate/source_selection.html'
    view_name = 'nominate'
    sub_view_name = 'nominate_source_selection'


class DisclaimerView(TemplateView):
    template_name = 'disclaimer.html'


class EmbedView(TemplateView):
    template_name = 'embed.html'

    def get_context_data(self, **kwargs):
        c = super(EmbedView, self).get_context_data(**kwargs)
        c['url'] = self.request.GET.get('img', '')
        return c


class ExtinctWebsitesView(MultiTableMixin, TemplateView):
    table_pagination = {"per_page": 20}

    TABLE_ATTRS = {
        'class': 'table table-sm table-striped table-hover'
    }

    def get(self, request, **kwargs):
        """
        Enable selected table export with Pandas
        """
        export = request.GET.get("export")
        export_format = request.GET.get("format", "csv").lower()
        # Ensure export filename will be safe
        if export_format not in ["csv", "xlsx"]:
            raise Http404()
        if export:
            try:
                # Raises if non-int or out-of-range is passed
                table = self.tables[int(export)]
                df = pd.DataFrame(table.as_values())
                # Use first row as columns
                df.columns = df.iloc[0]
                df = df.iloc[1:].sort_index()
                # Generate response filled with CSV data
                response = HttpResponse(content_type="text/csv")
                filename = (f"export-{export}_{date.today():%Y-%m-%d}"
                            f".{export_format}")
                response["Content-Disposition"] = \
                    f"attachment; filename={filename}"
                if export_format == "xlsx":
                    df.to_excel(response, index=False)
                else:
                    df.to_csv(response, index=False)
                return response
            except:
                raise Http404()
        else:
            return super().get(request, **kwargs)


class ExtinctWebsitesSummaryView(ExtinctWebsitesView):
    template_name = "extinct_websites/summary.html"

    tables = [
        ExtinctWebsitesTable(
            models.ExtinctWebsite.objects.filter(status_dead=True),
            attrs={**ExtinctWebsitesView.TABLE_ATTRS,
                   "pagination_id": "extinct"}),
        ExtinctWebsitesTable(
            models.ExtinctWebsite.objects.all(),
            attrs={**ExtinctWebsitesView.TABLE_ATTRS,
                   "pagination_id": "all"}),
    ]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ew_dead = EW.objects.filter(status_dead=True)

        ctx["start_date"] = EW.objects.aggregate(
            x=Min("date_monitoring_start"))["x"]
        ctx["total_records"] = EW.objects.all().count()
        ctx["num_dead"] = ew_dead.count()
        ctx["percentage_dead"] = (
            (ctx["num_dead"]/ctx["total_records"])*100
            if ctx["total_records"] > 0 else 0)
        ctx["last_updated_date"] = EW.objects.aggregate(
            x=Max("status_date"))["x"]
        # List of years from {last year} to 2020, reversed
        ctx["history_years"] = range(date.today().year - 1, 2019, -1)

        data = (EW.objects
                .filter(date_extinct__isnull=False)
                .annotate(date=TruncDay('date_extinct'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date'))

        chart_data = [{'date': entry['date'].strftime('%Y-%m-%d'),
                       'count': entry['count']} for entry in data]

        ctx['chart_data'] = chart_data

        return ctx


class ExtinctWebsitesHistoryView(ExtinctWebsitesView):
    template_name = "extinct_websites/history.html"

    def get(self, request, **kwargs):
        self.year = kwargs.get("year")
        self.tables = self.get_tables()  # must evaluate
        return super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["year"] = self.year
        ctx["last_updated_date"] = EW.objects.aggregate(
            x=Max("status_date"))["x"]
        return ctx

    def get_tables(self):
        return [
            ExtinctWebsitesTable(
                models.ExtinctWebsite.objects.filter(
                    date_monitoring_start__year__lte=self.year,
                    status_dead=True, date_extinct__year=self.year),
                attrs={**ExtinctWebsitesView.TABLE_ATTRS,
                       "pagination_id": "extinct"}),
            ExtinctWebsitesTable(
                models.ExtinctWebsite.objects.filter(
                    date_monitoring_start__year__lte=self.year),
                attrs={**ExtinctWebsitesView.TABLE_ATTRS,
                       "pagination_id": "all"}),
        ]
