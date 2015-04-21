import time
import models
import constants

from django import forms
from django.forms.util import ErrorDict
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.translation import ugettext_lazy as _


class CommentSecurityForm(forms.Form):
    """
    Handles the security aspects (anti-spoofing) for comment forms.
    """
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_pk = forms.CharField(widget=forms.HiddenInput)
    timestamp = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40,
                                    widget=forms.HiddenInput)

    honeypot = forms.CharField(required=False,
                               widget=forms.HiddenInput,
                               label=_('If you enter anything in this field '
                                       'your comment will be treated as spam'))

    def __init__(self, target_object, data=None, initial=None):
        self.target_object = target_object
        self.ct_type = ContentType.objects.get_for_model(target_object)

        if initial is None:
            initial = {}
        initial.update(self.generate_security_data())
        super(CommentSecurityForm, self).__init__(data=data, initial=initial)

    def security_errors(self):
        """
        Return just those errors associated with security
        """
        errors = ErrorDict()
        for f in ("honeypot", "timestamp", "security_hash"):
            if f in self.errors:
                errors[f] = self.errors[f]
        return errors

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
            content_type=self.data.get('content_type', ''),
            object_pk=self.data.get('object_pk', ''),
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
            'content_type': str(self.ct_type),
            'object_pk': str(self.target_object.pk),
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
        key_salt = "django.contrib.forms.CommentSecurityForm"
        value = "-".join(info)
        return salted_hmac(key_salt, value).hexdigest()


class AnonymousCommentForm(forms.ModelForm, CommentSecurityForm):
    """
    Comment form displayed to anonymous users
    """

    def save(self, commit=True):
        """
        Fills out object details received in initialization.
        """
        comment = super(AnonymousCommentForm, self).save(commit=False)
        comment.content_type = self.ct_type
        comment.object_pk = self.target_object.pk

    class Meta:
        model = models.Comment
        fields = ('user_name', 'user_email', 'comment')


class RegisteredCommentForm(AnonymousCommentForm):
    """
    Comment form for registered users
    """
    class Meta:
        model = models.Comment
        fields = ('comment',)