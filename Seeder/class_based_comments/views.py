import forms

from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin

from models import Comment


class CommentView(SingleObjectMixin, View):
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



    def get_context_data(self, **kwargs):
        context = super(CommentView, self).get_context_data(**kwargs)
        obj = self.get_object()
        form_class = self.get_form()
        context['comments'] = Comment.objects.for_model(self.get_object())
        context[self.form_name] = form_class(target_object=obj)
        return context

    def get_form(self, form_class=None):
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

    def form_valid(self, form):
        user = self.request.user
        comment = form.save(commit=False)
        if user.is_authenticated():
            comment.user = user
        comment.save()