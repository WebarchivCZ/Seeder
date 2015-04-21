from django.conf import settings

# default max length of comment in characters
COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)

# time window that can be used for commenting without reloading the page
COMMENT_TOKEN_EXPIRY = getattr(settings, 'COMMENT_MAX_LENGTH', 2 * 60 * 60)
