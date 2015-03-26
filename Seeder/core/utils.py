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


class ProjectPage(TemplateView):
    """
    This is used for easy declaration of titles and view_name that are used in
    menus to set current menu to active state.
    """
    title = 'Project'
    view_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(ProjectPage, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['view_name'] = self.view_name
        return context


class MultipleFormView(TemplateView):
    """
    View mixin that handles multiple forms / formsets.
    After the successful data is inserted ``self.process_forms`` is called.
    """
    form_classes = {}

    def get_context_data(self, **kwargs):
        context = super(MultipleFormView, self).get_context_data(**kwargs)
        forms_initialized = {name: form(prefix=name)
                             for name, form in self.form_classes.items()}

        return merge_dicts(context, forms_initialized)

    def post(self, request):
        forms_initialized = {
            name: form(prefix=name, data=request.POST)
            for name, form in self.form_classes.items()}

        valid = all([form_class.is_valid()
                     for form_class in forms_initialized.values()])
        if valid:
            return self.process_forms(forms_initialized)
        else:
            context = merge_dicts(self.get_context_data(), forms_initialized)
            return self.render_to_response(context)

    def process_forms(self, form_instances):
        raise NotImplemented
