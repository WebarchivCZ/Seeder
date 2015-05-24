"""
    Shared generic views used across the modules
"""

import reversion

from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.utils.translation import ugettext as _
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView

from django_tables2 import SingleTableView
from utils import dict_diff


class LoginMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginMixin, self).dispatch(request, *args, **kwargs)


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

    def post(self, request, *args, **kwargs):
        if self.permission and not request.user.has_perm(self.permission):
            self.add_message(_('Insufficient permissions.'), messages.ERROR)
        else:
            action = request.POST.get('action', None)
            if action in self.allowed_actions:
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


class HistoryView(DetailView):
    """
        Simple generic view for django reversion history
    """
    template_name = 'history.html'

    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        versions = reversion.get_unique_for_object(self.get_object())
        diffs = []
        if len(versions) > 1:
            for i in range(len(versions) - 1):
                new = versions[i]
                old = versions[i+1]
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


class FilteredListView(SingleTableView):
    """
        Abstract view class for list views with filters
    """
    template_name = 'filtered_list.html'
    context_object_name = 'objects'
    table_pagination = {"per_page": 20}

    table_class = NotImplemented
    filter_class = NotImplemented

    def get_table_data(self):
        queryset = super(FilteredListView, self).get_table_data()
        return self.filter_class(self.request.GET, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super(FilteredListView, self).get_context_data(**kwargs)
        context['filter'] = self.filter_class(data=self.request.GET)
        context['filter_active'] = bool(self.request.GET)
        return context
