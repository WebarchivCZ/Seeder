import forms

from django.http.response import HttpResponseRedirect
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin

from models import Comment


class CommentView(TemplateResponseMixin, SingleObjectMixin, View):
    """
    View for creating and listing comments.
    """
    anonymous_comment_form = forms.AnonymousCommentForm
    registered_comment_form = forms.RegisteredCommentForm
    anonymous_threaded_comment_form = forms.AnonymousThreadedCommentForm
    registered_threaded_comment_form = forms.RegisteredThreadedCommentForm

    # disable comments for anonymous users
    enforce_login = False
    # enable threading of comments
    threaded = False
    form_name = 'comment_form'

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
        authenticated = self.request.user.is_authenticated()
        if self.enforce_login and not authenticated:
            raise NotImplemented('Report a bug to show interest in this '
                                 'feature...')
        if self.threaded:
            if authenticated:
                return self.registered_threaded_comment_form
            return self.anonymous_threaded_comment_form
        else:
            if authenticated:
                return self.registered_comment_form
            return self.anonymous_comment_form