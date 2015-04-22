import forms

from django.http.response import HttpResponseRedirect
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin

from models import Comment


class CommentView(TemplateResponseMixin, SingleObjectMixin, View):
    """
    View for creating and listing comments.
    """

    # set to true if some of your users are anonymous
    anonymous = False
    # enable threading of comments
    threaded = False
    # form variable in templates
    form_name = 'comment_form'
    # enable titles in form
    titles = False


    def initialize_form(self, data=None):
        """
        This might be overridden if default does not accept target_object
        argument
        """
        return self.comment_form(target_object=self.get_object(), data=data)

    def post(self, request, **kwargs):

        form = self.initialize_form(data=request.POST)
        user = self.request.user

        if form.is_valid():
            comment = form.save(commit=False)
            if user.is_authenticated():
                comment.user = user
            comment.save()
            return HttpResponseRedirect('')  # reload the page
        else:
            context = self.get_context_data(**kwargs)
            context[self.form_name] = form
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CommentView, self).get_context_data(**kwargs)
        context['comments'] = Comment.objects.for_model(self.get_object())
        context[self.form_name] = self.initialize_form()
        return context

    @property
    def comment_form(self):
        return forms.create_form_class(self.threaded, self.anonymous,
                                       self.titles)