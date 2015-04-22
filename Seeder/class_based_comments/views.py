import forms

from django.views.generic.edit import CreateView


class CommentView(CreateView):
    """
    View for creating and listing comments.
    """
    anonymous_comment_form = forms.AnonymousCommentForm
    registered_comment_form = forms.RegisteredCommentForm
    anonymous_threaded_comment_form = forms.AnonymousThreadedCommentForm
    registered_threaded_comment_form = forms.RegisteredThreadedCommentForm

    prefix = 'comments'
    threaded = False
    # disable comments for anonymous users
    enforce_login = False

    def get_form(self, form_class=None):
        authenticated = self.request.user.is_authenticated()

        if self.enforce_login and not authenticated:
            raise NotImplemented('Report a bug to show interest in this '
                                 'feature... :P')

        if self.threaded:
            if authenticated:
                return self.registered_threaded_comment_form
            return self.anonymous_threaded_comment_form
        else:
            if authenticated:
                return self.registered_comment_form
            return self.anonymous_comment_form