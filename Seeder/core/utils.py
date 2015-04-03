from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


def merge_dicts(x, y):
    """
    Given two dicts, merge them into a new dict as a shallow copy.
    """
    z = x.copy()
    z.update(y)
    return z


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
        valid = all([form_class.is_valid() for name, form_class in forms_initialized.items()])
        if valid:
            return self.forms_valid(forms_initialized)
        else:
            context = merge_dicts(self.get_context_data(), forms_initialized)
            return self.render_to_response(context)

    def forms_valid(self, form_instances):
        raise NotImplemented