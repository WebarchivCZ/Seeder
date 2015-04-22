import time
import models
import constants

from django import forms
from django.shortcuts import get_object_or_404
from django.forms.utils import ErrorDict
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.translation import ugettext_lazy as _

CommentModel = models.Comment


class CommentSecurityForm(forms.ModelForm):
    """
    Handles the security aspects (anti-spoofing) for comment forms.
    """
    timestamp = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40,
                                    widget=forms.HiddenInput)

    honeypot = forms.CharField(required=False,
                               widget=forms.HiddenInput,
                               label=_('If you enter anything in this field '
                                       'your comment will be treated as spam'))

    def __init__(self, target_object, initial=None, **kwargs):
        self.target_object = target_object
        self.ct_type = ContentType.objects.get_for_model(target_object)

        if initial is None:
            initial = {}
        initial.update(self.generate_security_data())
        super(CommentSecurityForm, self).__init__(initial=initial, **kwargs)

    def clean_honeypot(self):
        """
        Check honeypot, this might detect simple spam bots
        """
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError(self.fields["honeypot"].label)
        return value

    def clean_security_hash(self):
        """
        Check the security hash
        """
        hash_received = self.cleaned_data["security_hash"]
        expected_hash = self.generate_security_hash(
            content_type=str(self.ct_type),
            object_pk=str(self.target_object.pk),
            timestamp=self.data.get('timestamp', ''),)
        if not constant_time_compare(expected_hash, hash_received):
            raise forms.ValidationError("Security hash check failed.")
        return hash_received

    def clean_timestamp(self):
        """
        Make sure the timestamp isn't too far (> 2 hours) in the past.
        """
        ts = self.cleaned_data["timestamp"]
        if time.time() - ts > constants.COMMENT_TOKEN_EXPIRY:
            raise forms.ValidationError("Timestamp check failed")
        return ts

    def generate_security_data(self):
        """Generate a dict of security data for "initial" data."""
        timestamp = int(time.time())
        return {
            'timestamp': str(timestamp),
            'security_hash': self.initial_security_hash(timestamp),
        }

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """

        return self.generate_security_hash(
            content_type=str(self.ct_type),
            object_pk=str(self.target_object.pk),
            timestamp=str(timestamp),
        )

    @staticmethod
    def generate_security_hash(content_type, object_pk, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        info = (content_type, object_pk, timestamp)
        key_salt = "CommentSecurityForm"
        value = "-".join(info)
        return salted_hmac(key_salt, value).hexdigest()


SECURITY_FIELDS = ('timestamp', 'security_hash', 'honeypot')


class CommentForm(CommentSecurityForm):
    """
    Mixin for comments form
    """

    def save(self, commit=True):
        """
        Fills out object details received in initialization.
        Note: super means 'Next in line' in this context:
            https://www.youtube.com/watch?v=EiOglTERPEo
        """
        comment = super(CommentForm, self).save(commit=False)
        comment.content_type = self.ct_type
        comment.object_pk = self.target_object.pk
        if commit:
            comment.save()
        return comment


class ThreadedCommentForm(CommentForm):
    """
    Mixin for threaded comments, contains hidden input for pk of the parent
    """
    parent = forms.IntegerField(widget=forms.HiddenInput)

    def save(self, commit=True):
        comment = super(ThreadedCommentForm, self).save(commit=False)
        comment.parent = get_object_or_404(CommentModel,
                                           pk=self.cleaned_data['parent'])
        if commit:
            comment.save()
        return comment


class AnonymousCommentForm(CommentForm):
    """
    Comment form displayed to anonymous users
    """

    class Meta:
        model = CommentModel
        fields = SECURITY_FIELDS + ('user_name', 'user_email', 'comment')


class RegisteredCommentForm(CommentForm):
    """
    Comment form for registered users
    """
    class Meta:
        model = CommentModel
        fields = SECURITY_FIELDS + ('comment',)


class AnonymousThreadedCommentForm(ThreadedCommentForm):
    """
    Threaded comment form displayed to anonymous users
    """

    class Meta:
        model = CommentModel
        fields = SECURITY_FIELDS + ('user_name', 'user_email', 'comment',
                                    'parent')


class RegisteredThreadedCommentForm(ThreadedCommentForm):
    """
    Threaded comment form for registered users
    """
    class Meta:
        model = CommentModel
        fields = SECURITY_FIELDS + ('comment', 'parent')