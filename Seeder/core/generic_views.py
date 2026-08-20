"""
    Shared generic views used across the modules
"""

from django.contrib import messages
from django.utils import timezone
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import View, ContextMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import SingleObjectMixin

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin

from reversion.models import Version

from .utils import dict_diff


class LoginMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class MessageView(object):
    """
        Simple view for making it easier to work with Message framework.
    """

    def add_message(self, message, level=messages.INFO):
        messages.add_message(self.request, level, message)


class ActionView(View, MessageView):
    """
    View for processing actions etc.
    """
    allowed_actions = ()
    # required permission for doing any kind of action
    permission = None

    action = NotImplemented

    def process_action(self, action):
        """
        Override this method
        """
        raise NotImplementedError('You must implement this method')

    def get_success_url(self):
        """
        This method will be used when action is successfully performed
        """
        raise NotImplementedError('Implement this!')

    def get_fail_url(self):
        """
        This method will be used when something goes awry.
        """
        raise NotImplementedError('Why would you not implement this?!')

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_fail_url())

    def check_permissions(self, user):
        return user.has_perm(self.permission) if self.permission else True

    def post(self, request, *args, **kwargs):
        if not self.check_permissions(request.user):
            self.add_message(_('Insufficient permissions.'), messages.ERROR)
        else:
            action = request.POST.get('action', None)
            if action in self.allowed_actions:
                self.action = action
                self.process_action(action)
                return HttpResponseRedirect(self.get_success_url())
            else:
                self.add_message(_('Action {0} not allowed.').format(action),
                                 messages.ERROR)
        return HttpResponseRedirect(self.get_fail_url())


class EditView(UpdateView, MessageView):
    template_name = 'edit_form.html'

    def form_valid(self, form):
        form.save()
        self.add_message(_('Changes successfully saved.'), messages.SUCCESS)
        return HttpResponseRedirect(self.get_object().get_absolute_url())


class ObjectMixinFixed(SingleObjectMixin):
    """
    This mixin can be used with login and form mixin
    """

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(*args, **kwargs)


class HistoryView(DetailView):
    """
        Simple generic view for django reversion history
    """
    template_name = 'history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        versions = Version.objects.get_for_object(self.get_object())
        diffs = []
        if len(versions) >= 1:
            for i in range(len(versions) - 1):
                new = versions[i]
                old = versions[i + 1]
                fields_changed = dict_diff(old.field_dict, new.field_dict)
                if fields_changed:
                    diffs.append({
                        'date': new.revision.date_created,
                        'user': new.revision.user,
                        'comment': new.revision.comment,
                        'fields_changed': fields_changed
                    })
        context['diffs'] = diffs
        context['versions'] = versions
        return context


class FilteredListView(ExportMixin, SingleTableMixin, FilterView):
    """
        Abstract view class for list views with filters
    """
    template_name = 'filtered_list.html'
    context_object_name = 'objects'
    table_pagination = {"per_page": 20}

    table_class = NotImplemented
    filterset_class = NotImplemented

    back_link = None
    back_link_title = _('Back')
    add_link = None
    add_link_title = _('Add')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_formats'] = ['csv', 'xlsx']
        context['filter'] = self.filterset_class(data=self.request.GET)
        context['filter_active'] = bool(self.request.GET)
        context['back_link'] = self.back_link
        context['back_link_title'] = self.back_link_title
        context['add_link'] = self.add_link
        context['add_link_title'] = self.add_link_title
        context['full_export_enabled'] = hasattr(
            self, "get_df_for_full_export")
        return context

    # ? def get_df_for_full_export(self) -> pd.DataFrame:
    # ? Implement in order to enable full export functionality

    def get_filename_for_export(self):
        return (f"{self.__class__.__name__.lower()}_"
                f"{timezone.now():%Y-%m-%d_%H-%M}.xlsx")

    def get(self, request, *args, **kwargs):
        """ Download all sources in an XLSX file """
        from django.http import HttpResponse, HttpRequest
        full_export = request.GET.get("full_export", "false").lower() == "true"
        if full_export and hasattr(self, "get_df_for_full_export"):
            df = self.get_df_for_full_export()
            if df is None:  # Not implemented, return default
                return super().get(request, *args, **kwargs)
            # Make datetime fields timezone-naive
            for col in df.columns:
                if df[col].dtype.name == "datetime64[ns, UTC]":
                    df[col] = df[col].dt.tz_convert("UTC").dt.tz_localize(None)
            # Export the DF straight into a downloading response
            filename = self.get_filename_for_export()
            response = HttpResponse(
                content_type=("application/vnd.openxmlformats-officedocument."
                              "spreadsheetml.sheet"))
            response["Content-Disposition"] = f"attachment; filename={filename}"
            df.to_excel(response, index=False, engine="openpyxl")
            return response
        return super().get(request, *args, **kwargs)


class JSONView(View, ContextMixin):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            safe=False,
            **response_kwargs
        )

    def get_data(self, context):
        raise NotImplementedError
