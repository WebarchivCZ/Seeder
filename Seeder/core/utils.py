from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.utils.translation import ugettext as _


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
                return HttpResponseRedirect(self.get_fail_url())
            else:
                self.add_message(_('Action {0} not allowed.').format(action),
                                 messages.ERROR)
        return HttpResponseRedirect(self.get_fail_url())
