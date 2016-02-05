import constants

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from managers import CommentManager


class Comment(MPTTModel):
    """
        User comment model
    """
    # Threading:
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True)

    # Content-object field
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('content type'),
        related_name="content_type_set_for_%(class)s")

    object_pk = models.TextField(_('object ID'))
    content_object = GenericForeignKey(ct_field="content_type",
                                       fk_field="object_pk")
    # Identity fields:
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_comments")
    user_name = models.CharField(_("user's name"), max_length=50, blank=True)
    user_email = models.EmailField(_("user's email address"), blank=True)

    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP address'),
        protocol='both',
        unpack_ipv4=True,
        blank=True,
        null=True)

    # optional title:
    title = models.CharField(
        verbose_name=_('Title'),
        max_length=64,
        blank=True
    )

    comment = models.TextField(
        verbose_name=_('comment'),
        max_length=constants.COMMENT_MAX_LENGTH)

    # Metadata about the comment
    submit_date = models.DateTimeField(_('date/time submitted'),
                                       auto_now_add=True, editable=False)
    last_changed = models.DateTimeField(auto_now=True, editable=False)

    is_public = models.BooleanField(
        verbose_name=_('is public'),
        default=True,
        help_text=_('Uncheck this box to make the comment effectively '
                    'disappear from the site.'))

    is_removed = models.BooleanField(
        verbose_name=_('is removed'),
        default=False,
        help_text=_('Check this box if the comment is inappropriate. A "This '
                    'comment has been removed" message will be displayed '
                    'instead.'))

    objects = CommentManager()

    def _get_user_info(self):
        """
        Get a dictionary that pulls together information about the poster
        safely for both authenticated and non-authenticated comments.
        This dict will have ``name``, ``email``, and ``url`` fields.
        """
        if not hasattr(self, "_user_info"):
            user_info = {
                "name": self.user_name,
                "email": self.user_email,
            }
            if self.user_id:
                u = self.user
                if u.email:
                    user_info["email"] = u.email

                # If the user has a full name, use that for the user name.
                # However, a given user_name overrides the raw user.username,
                # so only use that if this comment has no associated name.
                if u.get_full_name():
                    user_info["name"] = self.user.get_full_name()
                elif not self.user_name:
                    user_info["name"] = u.get_username()
            self._user_info = user_info
        return self._user_info
    user_info = property(_get_user_info)

    def _get_name(self):
        return self.user_info["name"]

    def _set_name(self, val):
        if self.user_id:
            raise AttributeError(_("Name of the registered user can't be "
                                   "changed"))
        self.user_name = val
    name = property(_get_name, _set_name, doc="Name of the author")

    def _get_email(self):
        return self.userinfo["email"]

    def _set_email(self, val):
        if self.user_id:
            raise AttributeError(_("E-mail of registered user can't be "
                                   "changed"))
        self.user_email = val
    email = property(_get_email, _set_email, doc="Email of the author")

    @property
    def text(self):
        """
            Property for safely showing comment content.
        """
        if self.is_removed:
            return _('This comment has been removed')
        return self.comment

    class MPTTMeta:
        order_insertion_by = ('submit_date',)

    class Meta:
        ordering = ('submit_date',)
        permissions = [("can_moderate", "Can moderate comments")]
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')