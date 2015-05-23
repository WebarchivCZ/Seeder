import reversion

from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.utils.translation import ugettext as _
from django.views.generic import DetailView


def merge_dicts(x, y):
    """
    Given two dicts, merge them into a new dict as a shallow copy.
    """
    z = x.copy()
    z.update(y)
    return z


def percentage(part, whole):
    """
    Simple utility for calculating percentages
    """
    return 100 * float(part) / float(whole)


def dict_diff(first, second):
    """
    >>> dict_diff({'a':'b', 'c':1}, {'a':'c', 'c':1})
    {'a': {'original':'b', 'changed': 'c'}

    :type first: dict
    :type second: dict
    :rtype dict
    """
    diff = {}
    keys = set(first.keys() + second.keys())
    for key in keys:
        first_value = first.get(key)
        second_value = second.get(key)
        if first_value != second_value:
            diff[key] = {
                'original': first_value,
                'changed': second_value
            }
    return diff


class LoginMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginMixin, self).dispatch(request, *args, **kwargs)


class MultipleFormView(TemplateView):
    """
    View mixin that handles multiple forms / formsets.
    After the successful data is inserted ``self.forms_valid`` is called.
    """
    form_classes = {}

    def initialize_forms(self, data=None):
        return {name: form(prefix=name, data=data)
                for name, form in self.form_classes.items()}

    def get_context_data(self, **kwargs):
        context = super(MultipleFormView, self).get_context_data(**kwargs)
        return merge_dicts(context, self.initialize_forms())

    def post(self, request):
        forms_initialized = self.initialize_forms(data=request.POST)
        valid = all([form.is_valid() for form in forms_initialized.values()])

        if valid:
            return self.forms_valid(forms_initialized)
        else:
            context = merge_dicts(self.get_context_data(), forms_initialized)
            return self.render_to_response(context)

    def forms_valid(self, form_instances):
        raise NotImplementedError('Implement this in your view!')


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


class HistoryView(DetailView):
    """
        Simple generic view for django reversion history
    """

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
